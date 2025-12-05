"""
Authentication Routes

Endpoints for API key management and authentication.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import secrets
import hashlib
from sqlalchemy.orm import Session

from middleware.auth import create_access_token, get_current_user, User, Role, require_admin
from db.session import get_session
from db.base import ApiKey

router = APIRouter()


class APIKeyRequest(BaseModel):
    """Request to create API key."""
    name: str
    expires_in_days: Optional[int] = 90


class APIKeyResponse(BaseModel):
    """API key response."""
    api_key: str
    expires_at: str


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
) -> APIKeyResponse:
    """
    Create a new API key.
    
    Requires admin role.
    """
    # Generate API key
    api_key = f"pk_{secrets.token_urlsafe(32)}"
    
    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
    
    # Persist hashed key
    key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    db.add(ApiKey(name=request.name, key_hash=key_hash, expires_at=expires_at, created_by=current_user.email))
    db.commit()

    return APIKeyResponse(api_key=api_key, expires_at=expires_at.isoformat() + "Z")


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get current user information."""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "roles": [role.value for role in current_user.roles]
    }
