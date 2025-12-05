"""
Authentication Routes

Endpoints for API key management and authentication.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import secrets

from middleware.auth import create_access_token, get_current_user, User, Role, require_admin

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
    current_user: User = Depends(require_admin)
) -> APIKeyResponse:
    """
    Create a new API key.
    
    Requires admin role.
    """
    # Generate API key
    api_key = f"pk_{secrets.token_urlsafe(32)}"
    
    # Calculate expiration
    expires_in_days = request.expires_in_days if request.expires_in_days is not None else 90
    if expires_in_days <= 0:
        raise HTTPException(status_code=400, detail="expires_in_days must be positive")
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    # TODO: Store API key in database with user association
    # For now, return the key (in production, hash and store)
    
    return APIKeyResponse(
        api_key=api_key,
        expires_at=expires_at.isoformat() + "Z"
    )


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
