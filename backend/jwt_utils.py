"""JWT token generation and verification utilities."""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 days


def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token for user."""
    logger.debug("--- create_access_token called ---")
    logger.debug(f"User ID: {user_id}")
    logger.debug(f"Email: {email}")
    logger.debug(f"Algorithm: {ALGORITHM}")
    logger.debug(f"Expire minutes: {EXPIRE_MINUTES}")

    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    logger.debug(f"Token will expire at: {expire.isoformat()}")

    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    logger.debug(f"Payload to encode: {to_encode}")

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"JWT token created successfully (length: {len(encoded_jwt)})")
        logger.debug(f"Token preview: {encoded_jwt[:50]}...")
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT encoding error: {type(e).__name__}: {str(e)}")
        raise


def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token and return payload if valid."""
    logger.debug("--- verify_token called ---")
    logger.debug(f"Token length: {len(token)}")
    logger.debug(f"Token preview: {token[:50]}...")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token decoded successfully. Payload: {payload}")

        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        logger.debug(f"Extracted user_id: {user_id}")
        logger.debug(f"Extracted email: {email}")

        if user_id is None or email is None:
            logger.warning("Token payload missing user_id or email")
            return None

        logger.debug("Token verification successful")
        return {"user_id": user_id, "email": email}
    except JWTError as e:
        logger.error(f"JWT verification error: {type(e).__name__}: {str(e)}")
        return None


def decode_token(token: str) -> Optional[str]:
    """Decode JWT token and return user_id if valid."""
    payload = verify_token(token)
    if payload:
        return payload["user_id"]
    return None
