import logging

from datetime import timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User
from app.auth.auth import (
    create_access_token,
    get_password_hash,
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.database.db import SessionLocal

router = APIRouter(prefix="/auth", tags=["auth"])

# Setting up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Dependency: get a database session
def get_db():
    """
    Dependency to retrieve a database session for performing database operations.
    The session is automatically closed after the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Request schemas for signup, login, and user deletion
class SignupRequest(BaseModel):
    """Schema for user signup request."""

    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Schema for user login request."""

    username: str
    password: str


class AuthRequest(BaseModel):
    """Schema for user authentication request (e.g., for login)."""

    username: str
    password: str


class DeleteUserRequest(BaseModel):
    """Schema for deleting a user."""

    username: str
    password: str


@router.post("/signup")
def signup(user_info: SignupRequest, db: Session = Depends(get_db)):
    """
    Signs up a new user by creating a new record in the database.
    It checks for existing usernames and emails before creating a new user.

    Args:
    - user_info (SignupRequest): The information for creating a new user.

    Raises:
    - HTTPException: If the username or email already exists.

    Returns:
    - dict: A message indicating successful creation of the user.
    """
    logger.info(f"Attempting to sign up user: {user_info.username}")

    # Check if username already exists
    if db.query(User).filter(User.username == user_info.username).first():
        logger.warning(f"Signup failed: Username {user_info.username} already exists.")
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    if db.query(User).filter(User.email == user_info.email).first():
        logger.warning(f"Signup failed: Email {user_info.email} already registered.")
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create and add the user to the database
    hashed_password = get_password_hash(user_info.password)
    user = User(
        username=user_info.username,
        email=user_info.email,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"User {user_info.username} created successfully.")
    return {"message": "User created successfully"}


@router.post("/login")
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticates a user using the provided username and password, and returns a JWT access token.

    Args:
    - db (Session): Database session.
    - form_data (OAuth2PasswordRequestForm): Contains username and password for authentication.

    Raises:
    - HTTPException: If the authentication fails due to invalid credentials.

    Returns:
    - dict: The access token and token type.
    """
    logger.info(f"Attempting to log in user: {form_data.username}")

    user = authenticate_user(db, form_data.username, form_data.password)

    # If authentication fails, log and raise an error
    if not user:
        logger.warning(
            f"Login failed for user: {form_data.username}. Invalid credentials."
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate and return the JWT access token
    access_token = create_access_token(data={"sub": user.username})

    logger.info(f"User {form_data.username} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}


@router.delete("/delete")
def delete_user(user_info: DeleteUserRequest, db: Session = Depends(get_db)):
    """
    Deletes a user after authenticating their credentials.

    Args:
    - user_info (DeleteUserRequest): Contains username and password for deleting the user.

    Raises:
    - HTTPException: If authentication fails due to invalid credentials.

    Returns:
    - dict: A message indicating successful deletion of the user.
    """
    logger.info(f"Attempting to delete user: {user_info.username}")

    # Authenticate the user before deletion
    user = authenticate_user(db, user_info.username, user_info.password)

    # If authentication fails, log and raise an error
    if not user:
        logger.warning(
            f"Deletion failed: Invalid credentials for user {user_info.username}."
        )
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Delete the user from the database
    db.delete(user)
    db.commit()

    logger.info(f"User {user_info.username} deleted successfully.")
    return {"message": "User deleted successfully"}
