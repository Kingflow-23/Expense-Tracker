from datetime import timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException

from app.database.db import SessionLocal
from app.models.user import User
from app.auth.auth import (
    create_access_token,
    get_password_hash,
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# Dependency: get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Request schemas for signup and login
class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/signup")
def signup(user_info: SignupRequest, db: Session = Depends(get_db)):
    # Check if username or email already exists
    if db.query(User).filter(User.username == user_info.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == user_info.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_info.password)
    user = User(
        username=user_info.username,
        email=user_info.email,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}


@router.post("/login")
def login(user_info: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_info.username, user_info.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}
