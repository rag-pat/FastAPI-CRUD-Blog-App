from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

# Base schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class PostBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    published: bool = False
    featured_image_url: Optional[str] = None

class CommentBase(BaseModel):
    content: str

class TagBase(BaseModel):
    name: str

# Create schemas
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_complexity(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v

class PostCreate(PostBase):
    tag_ids: Optional[List[int]] = []

class CommentCreate(CommentBase):
    pass

class TagCreate(TagBase):
    pass

# Update schemas
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    profile_image_url: Optional[str] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    published: Optional[bool] = None
    featured_image_url: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class CommentUpdate(BaseModel):
    content: Optional[str] = None

# Response schemas
class Tag(TagBase):
    id: int
    
    class Config:
        orm_mode = True

class Comment(CommentBase):
    id: int
    post_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class User(UserBase):
    id: int
    profile_image_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class Post(PostBase):
    id: int
    slug: str
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    view_count: int
    owner: User
    tags: List[Tag] = []
    
    class Config:
        orm_mode = True

class PostDetail(Post):
    comments: List[Comment] = []

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime
    user: User

class TokenPayload(BaseModel):
    sub: str
    exp: int
    jti: str

# File upload schema
class FileUploadResponse(BaseModel):
    file_url: str
    content_type: str
    file_size: int
