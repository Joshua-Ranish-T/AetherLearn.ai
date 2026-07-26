"""
Authentication Dependency — Firebase Auth ID Token Verification.

Provides `get_current_user` and `get_optional_user` FastAPI dependencies.
Ensures zero disruption to local development by falling back to a dev user when REQUIRE_AUTH=false.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError
from app.core.logging_config import get_logger
from app.core.firebase import is_firebase_initialized

logger = get_logger(__name__)
settings = get_settings()

security_bearer = HTTPBearer(auto_error=False)

DEFAULT_DEV_USER: Dict[str, Any] = {
    "uid": "local_dev_user",
    "email": "dev@localhost",
    "name": "Local Developer",
    "picture": "",
}


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
) -> Optional[Dict[str, Any]]:
    """
    Attempt to extract and verify Firebase Auth token if provided.
    Returns user dict if valid, None otherwise.
    """
    if not credentials or not credentials.credentials:
        return DEFAULT_DEV_USER if not settings.require_auth else None

    token = credentials.credentials
    if not is_firebase_initialized():
        logger.warning("Firebase not initialized; falling back to dev user for auth")
        return DEFAULT_DEV_USER if not settings.require_auth else None

    try:
        from firebase_admin import auth as firebase_auth
        decoded_token = firebase_auth.verify_id_token(token)
        return {
            "uid": decoded_token.get("uid", ""),
            "email": decoded_token.get("email", ""),
            "name": decoded_token.get("name", ""),
            "picture": decoded_token.get("picture", ""),
        }
    except Exception as exc:
        logger.warning("Token verification failed", error=str(exc))
        if not settings.require_auth:
            return DEFAULT_DEV_USER
        return None


async def get_current_user(
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
) -> Dict[str, Any]:
    """
    FastAPI dependency requiring a valid authenticated user.
    When REQUIRE_AUTH is false, falls back to DEFAULT_DEV_USER so existing local workflows never break.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in with Google.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
