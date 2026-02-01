"""Authentication routes for signup and login."""

import re
import bcrypt
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models import User
from db import get_session
from jwt_utils import create_access_token
from pydantic import BaseModel, constr
from typing import Optional
from middleware.jwt_auth import get_current_user_id

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# bcrypt has a 72-byte limit for passwords
MAX_PASSWORD_LENGTH = 72

# Task reference: T026d (Fix bcrypt/passlib compatibility in backend)


# Pydantic models for validation
class UserCreate(BaseModel):
    email: constr(min_length=1, max_length=255)
    password: constr(min_length=8, max_length=MAX_PASSWORD_LENGTH)
    name: Optional[constr(max_length=255)] = None


class UserLogin(BaseModel):
    email: constr(min_length=1, max_length=255)
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: str


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


class UserUpdate(BaseModel):
    name: Optional[constr(max_length=255)] = None
    email: Optional[constr(min_length=1, max_length=255)] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: constr(min_length=8, max_length=MAX_PASSWORD_LENGTH)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Notes:
    - bcrypt only uses the first 72 bytes of the password. We enforce this limit
      to avoid silent truncation.

    Task reference: T026d (Fix bcrypt/passlib compatibility in backend)
    """
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password exceeds maximum length of {MAX_PASSWORD_LENGTH} bytes")

    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash.

    Task reference: T026d (Fix bcrypt/passlib compatibility in backend)
    """
    logger.debug("--- verify_password called ---")
    logger.debug(f"Plain password length: {len(plain_password)}")
    logger.debug(f"Hashed password: {hashed_password[:20]}... (truncated)")

    try:
        plain_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")

        logger.debug(f"Plain password bytes length: {len(plain_bytes)}")
        logger.debug(f"Hash bytes length: {len(hash_bytes)}")

        result = bcrypt.checkpw(plain_bytes, hash_bytes)
        logger.debug(f"bcrypt.checkpw result: {result}")

        return result
    except Exception as e:
        logger.error(f"Exception in verify_password: {type(e).__name__}: {str(e)}")
        raise


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    """Create a new user account."""
    logger.debug("=" * 60)
    logger.debug("SIGNUP REQUEST RECEIVED")
    logger.debug(f"Email: {user_data.email}")
    logger.debug(f"Name: {user_data.name}")
    logger.debug(f"Password length: {len(user_data.password)} characters")
    logger.debug("=" * 60)

    # Validate email
    logger.debug(f"Validating email format: {user_data.email}")
    if not validate_email(user_data.email):
        logger.warning(f"Invalid email format: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    logger.debug("Email format is valid")

    # Check if user already exists
    logger.debug(f"Checking if user already exists: {user_data.email}")
    existing_user = (await session.exec(
        select(User).where(User.email == user_data.email)
    )).first()

    if existing_user:
        logger.warning(f"User already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    logger.debug("User does not exist, proceeding with signup")

    # Create new user
    logger.debug("Hashing password...")
    try:
        hashed_password = hash_password(user_data.password)
        logger.debug(f"Password hashed successfully (length: {len(hashed_password)})")
    except ValueError as e:
        logger.error(f"Password hashing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    logger.debug("Creating new user in database...")
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    logger.debug(f"User created successfully: ID={new_user.id}")

    # Generate JWT token
    logger.debug(f"Generating JWT token for new user: {new_user.id}")
    try:
        token = create_access_token(new_user.id, new_user.email)
        logger.debug(f"JWT token generated successfully (length: {len(token)})")
    except Exception as e:
        logger.error(f"JWT token generation error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authentication token"
        )

    logger.debug("Signup successful! Returning response...")
    logger.debug("=" * 60)

    return TokenResponse(
        token=token,
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            created_at=new_user.created_at.isoformat()
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, session: AsyncSession = Depends(get_session)):
    """Login an existing user."""
    logger.debug("=" * 60)
    logger.debug("LOGIN REQUEST RECEIVED")
    logger.debug(f"Email: {user_data.email}")
    logger.debug(f"Password length: {len(user_data.password)} characters")
    logger.debug("=" * 60)

    # Find user by email
    logger.debug(f"Searching for user with email: {user_data.email}")
    user = (await session.exec(
        select(User).where(User.email == user_data.email)
    )).first()

    if not user:
        logger.warning(f"User not found with email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    logger.debug(f"User found: ID={user.id}, Email={user.email}, Name={user.name}")
    logger.debug(f"Stored password hash length: {len(user.password_hash)} characters")

    # Verify password
    logger.debug("Starting password verification...")
    try:
        password_valid = verify_password(user_data.password, user.password_hash)
        logger.debug(f"Password verification result: {password_valid}")

        if not password_valid:
            logger.warning(f"Password verification failed for user: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
    except Exception as e:
        logger.error(f"Password verification error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    logger.debug("Password verification successful!")

    # Generate JWT token
    logger.debug(f"Generating JWT token for user: {user.id}")
    try:
        token = create_access_token(user.id, user.email)
        logger.debug(f"JWT token generated successfully (length: {len(token)})")
    except Exception as e:
        logger.error(f"JWT token generation error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authentication token"
        )

    logger.debug("Login successful! Returning response...")
    logger.debug("=" * 60)

    return TokenResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at.isoformat()
        )
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Update user profile (name and/or email)."""
    logger.debug("=" * 60)
    logger.debug("UPDATE PROFILE REQUEST RECEIVED")
    logger.debug(f"User ID: {current_user_id}")
    logger.debug(f"Update data: name={user_data.name}, email={user_data.email}")
    logger.debug("=" * 60)

    # Get current user
    user = await session.get(User, current_user_id)
    if not user:
        logger.error(f"User not found: {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update name if provided
    if user_data.name is not None:
        logger.debug(f"Updating name from '{user.name}' to '{user_data.name}'")
        user.name = user_data.name

    # Update email if provided
    if user_data.email is not None and user_data.email != user.email:
        logger.debug(f"Updating email from '{user.email}' to '{user_data.email}'")

        # Validate email format
        if not validate_email(user_data.email):
            logger.warning(f"Invalid email format: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )

        # Check if email is already taken
        existing_user = (await session.exec(
            select(User).where(User.email == user_data.email)
        )).first()

        if existing_user and existing_user.id != current_user_id:
            logger.warning(f"Email already taken: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user.email = user_data.email

    # Save changes
    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.debug("Profile updated successfully!")
    logger.debug("=" * 60)

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at.isoformat()
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Change user password."""
    logger.debug("=" * 60)
    logger.debug("CHANGE PASSWORD REQUEST RECEIVED")
    logger.debug(f"User ID: {current_user_id}")
    logger.debug("=" * 60)

    # Get current user
    user = await session.get(User, current_user_id)
    if not user:
        logger.error(f"User not found: {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify current password
    logger.debug("Verifying current password...")
    if not verify_password(password_data.current_password, user.password_hash):
        logger.warning("Current password verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    logger.debug("Current password verified successfully")

    # Hash new password
    logger.debug("Hashing new password...")
    try:
        new_password_hash = hash_password(password_data.new_password)
        logger.debug("New password hashed successfully")
    except ValueError as e:
        logger.error(f"Password hashing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Update password
    user.password_hash = new_password_hash
    session.add(user)
    await session.commit()

    logger.debug("Password changed successfully!")
    logger.debug("=" * 60)

    return {"message": "Password changed successfully"}
