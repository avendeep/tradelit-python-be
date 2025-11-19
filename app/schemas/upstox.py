"""
Pydantic schemas for Upstox authentication
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UpstoxLoginResponse(BaseModel):
    """Response schema for login URL generation"""

    login_url: str = Field(..., description="Upstox OAuth login URL")
    state: Optional[str] = Field(
        None, description="State parameter for CSRF protection"
    )


class UpstoxCallbackRequest(BaseModel):
    """Request schema for OAuth callback"""

    code: str = Field(..., description="Authorization code from Upstox")
    state: Optional[str] = Field(
        None, description="State parameter returned from OAuth flow"
    )


class UpstoxTokenResponse(BaseModel):
    """Response schema for access token"""

    access_token: str = Field(..., description="Upstox API access token")
    expires_in: int = Field(..., description="Token expiry time in seconds")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_at: str = Field(..., description="ISO format timestamp of token expiry")


class UpstoxUserProfile(BaseModel):
    """User profile schema"""

    user_id: Optional[str] = None
    user_name: Optional[str] = None
    email: Optional[str] = None
    user_type: Optional[str] = None
    poa: Optional[bool] = None
    is_active: Optional[bool] = None
    broker: Optional[str] = None
    products: Optional[list] = None
    exchanges: Optional[list] = None


class UpstoxAuthStatus(BaseModel):
    """Authentication status schema"""

    is_authenticated: bool = Field(..., description="Whether user is authenticated")
    token_valid: bool = Field(..., description="Whether access token is valid")
    expires_at: Optional[str] = Field(None, description="Token expiry timestamp")
    user_profile: Optional[UpstoxUserProfile] = Field(
        None, description="User profile if authenticated"
    )
