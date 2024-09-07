# Description: This file contains the security functions for the FastAPI application. I used a coding assistant when developing this script iteratively.

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from data_models import TokenData
from db import user_collection, user_helper
from fastapi.encoders import jsonable_encoder
from pymongo.errors import DuplicateKeyError


SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1200


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(username: str, password: str):
    user = await user_collection.find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


async def register_user(user_data: dict) -> dict:
    user_data["hashed_password"] = get_password_hash(user_data["password"])
    del user_data["password"]   
    user_data["username"] = user_data["email"]
    user_data["role"] = "user"
    user_data["is_activated"] = False

    try:
        new_user = await user_collection.insert_one(user_data)
        created_user = await user_collection.find_one({"_id": new_user.inserted_id})
        return user_helper(created_user)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email or username already exists")


def verify_password(plain_password, hashed_password):
    """
    Verify a plain password against a hashed version.

    Args:
    - plain_password (str): The plain text password to verify.
    - hashed_password (str): The hashed password to verify against.

    Returns:
    - bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Generate a hash for a given password.

    Args:
    - password (str): The plain text password to hash.

    Returns:
    - str: The hashed version of the input password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token with optional expiry.

    Args:
    - data (dict): The data to encode in the JWT.
    - expires_delta (Optional[timedelta]): The time delta for the token expiration.
      If None, defaults to 15 minutes.

    Returns:
    - str: The encoded JWT token as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user from a JWT token.

    Args:
    - token (str): The JWT token to decode.

    Returns:
    - TokenData: The user information extracted from the token.

    Raises:
    - HTTPException: If the token is invalid or the credentials cannot be validated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_active_user(current_user: TokenData = Depends(get_current_user)):
    """
    Validate the role of the current user.

    Args:
    - current_user (TokenData): The current user's data.

    Returns:
    - TokenData: The validated user data.

    Raises:
    - HTTPException: If the user's role is not valid.
    """
    if current_user.role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid user role")
    return current_user


# Dummy database of users
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("adminpassword"),
        "role": "admin",
    },
    "user": {
        "username": "user",
        "hashed_password": get_password_hash("userpassword"),
        "role": "user",
    },
}
