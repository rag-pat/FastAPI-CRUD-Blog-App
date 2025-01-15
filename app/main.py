from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from typing import List
from . import crud, models, schemas
from .database import get_db
from .auth import create_access_token, get_username_from_token
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize app
app = FastAPI()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    return crud.create_user(db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=form_data.username)
    if not db_user or not crud.verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/search/posts", response_model=List[schemas.Post])
def search_posts(query: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    posts = crud.search_posts(db, query=query, skip=skip, limit=limit)
    return posts

@app.get("/user/posts", response_model=List[schemas.Post])
def get_user_posts(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), skip: int = 0, limit: int = 10):
    username = get_username_from_token(token)
    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return crud.get_user_posts(db, user_id=db_user.id, skip=skip, limit=limit)

@app.get("/posts", response_model=List[schemas.Post])
@limiter.limit("5/minute")
def get_posts(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    success = crud.soft_delete_post(db, post_id=id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return {}
