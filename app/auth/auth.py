import os
import logging

from jose import JWTError, jwt
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from app.models.user import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Secret key and token settings
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that the plain password matches the hashed one.

    Args:
    - plain_password (str): The plain text password entered by the user.
    - hashed_password (str): The hashed password stored in the database.

    Returns:
    - bool: True if passwords match, False otherwise.
    """
    result = pwd_context.verify(plain_password, hashed_password)
    if result:
        logging.info("Password verification succeeded.")
    else:
        logging.warning("Password verification failed.")
    return result


def get_password_hash(password: str) -> str:
    """
    Hashes a password for secure storage.

    Args:
    - password (str): The plain password to be hashed.

    Returns:
    - str: The hashed password.
    """
    hashed = pwd_context.hash(password)
    logging.info("Password hashed successfully.")
    return hashed


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT access token with an expiration time.

    Args:
    - data (dict): The data to include in the token (e.g., user info).
    - expires_delta (timedelta, optional): The token expiration time. Defaults to 15 minutes.

    Returns:
    - str: The encoded JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logging.info("Access token created; expires at %s", expire.isoformat())
    return token


def get_user_by_username(db: Session, username: str):
    """
    Fetches a user from the database by their username.

    Args:
    - db (Session): The database session for querying the user.
    - username (str): The username to search for in the database.

    Returns:
    - User: The user object if found, otherwise None.
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        logging.info("User '%s' found in the database.", username)
    else:
        logging.info("User '%s' not found in the database.", username)
    return user


def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticates a user by their username and password.
    Returns the user object if authentication is successful,
    or None otherwise.

    Args:
    - db (Session): The database session for querying users.
    - username (str): The username entered by the user.
    - password (str): The password entered by the user.

    Returns:
    - User: The user object if authenticated, otherwise None.
    """
    logging.info("Attempting to authenticate user '%s'.", username)
    user = get_user_by_username(db, username)
    if not user:
        logging.warning("Authentication failed: user '%s' not found.", username)
        return None
    if not verify_password(password, user.hashed_password):
        logging.warning("Authentication failed: incorrect password for '%s'.", username)
        return None
    logging.info("User '%s' authenticated successfully.", username)
    return user
