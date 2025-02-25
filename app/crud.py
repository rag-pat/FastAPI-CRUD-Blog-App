from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional, Union, Tuple
import logging
from slugify import slugify

from . import models, schemas
from .security import get_password_hash, verify_password
from .aws import dynamodb_service, sqs_service

logger = logging.getLogger(__name__)

# User CRUD operations
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    # Check if username or email already exists
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name,
        is_active=user.is_active
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Send welcome notification to SQS
        sqs_service.send_notification(
            notification_type="user_registered",
            payload={"user_id": db_user.id, "username": db_user.username}
        )
        
        return db_user
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update user information"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # Update user attributes if provided
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update violates unique constraint"
        )

# Post CRUD operations
def create_post(db: Session, post: schemas.PostCreate, user_id: int) -> models.Post:
    """Create a new blog post"""
    # Generate slug from title
    base_slug = slugify(post.title)
    slug = base_slug
    counter = 1
    
    # Ensure slug is unique
    while db.query(models.Post).filter(models.Post.slug == slug).first() is not None:
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    db_post = models.Post(
        title=post.title,
        slug=slug,
        content=post.content,
        summary=post.summary,
        published=post.published,
        featured_image_url=post.featured_image_url,
        owner_id=user_id
    )
    
    # Add tags if provided
    if post.tag_ids:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(post.tag_ids)).all()
        db_post.tags = tags
    
    try:
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        # Send notification about new post
        if db_post.published:
            sqs_service.send_notification(
                notification_type="post_published",
                payload={
                    "post_id": db_post.id,
                    "title": db_post.title,
                    "author_id": db_post.owner_id
                }
            )
        
        return db_post
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error creating post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

def get_post_by_id(db: Session, post_id: int) -> Optional[models.Post]:
    """Get post by ID, only if not deleted"""
    return db.query(models.Post).filter(
        models.Post.id == post_id,
        models.Post.deleted_at == None
    ).first()

def get_post_by_slug(db: Session, slug: str) -> Optional[models.Post]:
    """Get post by slug, only if not deleted"""
    return db.query(models.Post).filter(
        models.Post.slug == slug,
        models.Post.deleted_at == None
    ).first()

def get_posts(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    published_only: bool = True,
    tag_id: Optional[int] = None
) -> List[models.Post]:
    """Get all posts with pagination and filtering"""
    query = db.query(models.Post).filter(models.Post.deleted_at == None)
    
    if published_only:
        query = query.filter(models.Post.published == True)
    
    if tag_id:
        query = query.join(models.Post.tags).filter(models.Tag.id == tag_id)
    
    # Order by created_at descending (newest first)
    return query.order_by(desc(models.Post.created_at)).offset(skip).limit(limit).all()

def search_posts(db: Session, query: str, skip: int = 0, limit: int = 10) -> List[models.Post]:
    """Search posts by title or content"""
    return db.query(models.Post).filter(
        models.Post.deleted_at == None,
        models.Post.published == True,
        or_(
            models.Post.title.ilike(f"%{query}%"),
            models.Post.content.ilike(f"%{query}%")
        )
    ).order_by(desc(models.Post.created_at)).offset(skip).limit(limit).all()

def get_user_posts(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> List[models.Post]:
    """Get all posts by user ID"""
    return db.query(models.Post).filter(
        models.Post.owner_id == user_id,
        models.Post.deleted_at == None
    ).order_by(desc(models.Post.created_at)).offset(skip).limit(limit).all()

def update_post(
    db: Session, 
    post_id: int, 
    post_update: schemas.PostUpdate, 
    user_id: int
) -> Optional[models.Post]:
    """Update a post"""
    db_post = get_post_by_id(db, post_id)
    if not db_post:
        return None
    
    # Check ownership
    if db_post.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    # Update slug if title changed
    if post_update.title and post_update.title != db_post.title:
        base_slug = slugify(post_update.title)
        slug = base_slug
        counter = 1
        
        # Ensure slug is unique
        while db.query(models.Post).filter(
            models.Post.slug == slug, 
            models.Post.id != post_id
        ).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        db_post.slug = slug
    
    # Update post attributes if provided
    update_data = post_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key != 'tag_ids':
            setattr(db_post, key, value)
    
    # Update tags if provided
    if post_update.tag_ids is not None:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(post_update.tag_ids)).all()
        db_post.tags = tags
    
    try:
        db.commit()
        db.refresh(db_post)
        
        # Send notification if post was published
        was_published = db_post.published and ('published' in update_data and update_data['published'])
        if was_published:
            sqs_service.send_notification(
                notification_type="post_updated",
                payload={
                    "post_id": db_post.id,
                    "title": db_post.title,
                    "author_id": db_post.owner_id
                }
            )
        
        return db_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update violates unique constraint"
        )

def soft_delete_post(db: Session, post_id: int, user_id: int) -> bool:
    """Soft delete a post (mark as deleted)"""
    db_post = get_post_by_id(db, post_id)
    if not db_post:
        return False
    
    # Check ownership
    if db_post.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    # Mark as deleted
    db_post.deleted_at = datetime.utcnow()
    
    try:
        db.commit()
        
        # Send notification
        sqs_service.send_notification(
            notification_type="post_deleted",
            payload={
                "post_id": db_post.id,
                "title": db_post.title,
                "author_id": db_post.owner_id
            }
        )
        
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Database error deleting post: {e}")
        return False

def increment_post_view(db: Session, post_id: int) -> bool:
    """Increment post view count using DynamoDB"""
    # Get current view count from DynamoDB
    new_view_count = dynamodb_service.increment_view_count(post_id)
    
    if new_view_count > 0:
        # Update SQL database periodically (not on every view)
        db_post = get_post_by_id(db, post_id)
        if db_post and (new_view_count - db_post.view_count >= 10 or new_view_count % 100 == 0):
            db_post.view_count = new_view_count
            db.commit()
        return True
    return False

# Comment CRUD operations
def create_comment(
    db: Session, 
    comment: schemas.CommentCreate, 
    post_id: int, 
    user_id: int
) -> models.Comment:
    """Create a new comment"""
    # Check if post exists
    db_post = get_post_by_id(db, post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_
