"""JWT token creation and verification."""
from datetime import timedelta
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings


def create_user_token(email: str) -> str:
    """
    Create a JWT token for a user.
    
    Args:
        email: User email to encode in token
        
    Returns:
        str: Encoded JWT token
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=access_token_expires
    )
    return access_token


def verify_token(token: str) -> dict | None:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        dict | None: Decoded token payload or None if invalid
    """
    return decode_access_token(token)
