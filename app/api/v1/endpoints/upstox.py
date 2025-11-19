"""
Upstox authentication endpoints
Implements OAuth 2.0 authentication flow
"""

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from typing import Optional
import secrets

from app.schemas.upstox import (
    UpstoxLoginResponse,
    UpstoxCallbackRequest,
    UpstoxTokenResponse,
    UpstoxAuthStatus,
    UpstoxUserProfile,
)
from app.services.upstox_service import upstox_service


router = APIRouter(prefix="/upstox", tags=["Upstox Authentication"])


@router.get("/login", response_model=UpstoxLoginResponse)
async def upstox_login():
    """
    Step 1: Generate Upstox OAuth login URL

    Returns the login URL that the user should be redirected to for authentication.
    The state parameter is generated for CSRF protection.
    """
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Get login URL from service
    login_url = upstox_service.get_login_url(state=state)

    return UpstoxLoginResponse(login_url=login_url, state=state)


@router.get("/callback")
async def upstox_callback(
    code: str = Query(..., description="Authorization code from Upstox"),
    state: Optional[str] = Query(
        None, description="State parameter for CSRF verification"
    ),
):
    """
    Step 2: OAuth callback endpoint

    This endpoint receives the authorization code from Upstox after user authentication.
    It exchanges the code for an access token.

    In production, you should verify the state parameter to prevent CSRF attacks.
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required",
        )

    try:
        # Exchange authorization code for access token
        token_data = await upstox_service.generate_access_token(code)

        return {"message": "Authentication successful", "token_data": token_data}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate with Upstox: {str(e)}",
        )


@router.post("/token", response_model=UpstoxTokenResponse)
async def generate_token(request: UpstoxCallbackRequest):
    """
    Step 2 (Alternative): Generate access token from authorization code

    This is an alternative to the callback endpoint for applications that
    prefer to handle the token exchange explicitly via POST request.
    """
    try:
        token_data = await upstox_service.generate_access_token(request.code)
        return UpstoxTokenResponse(**token_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate access token: {str(e)}",
        )


@router.get("/status", response_model=UpstoxAuthStatus)
async def get_auth_status():
    """
    Get current authentication status

    Returns whether the user is authenticated and if the token is still valid.
    Also includes user profile information if available.
    """
    is_valid = upstox_service.is_token_valid()
    access_token = upstox_service.get_access_token()

    user_profile = None
    if is_valid:
        profile_data = await upstox_service.get_user_profile()
        if profile_data:
            user_profile = UpstoxUserProfile(**profile_data.get("data", {}))

    return UpstoxAuthStatus(
        is_authenticated=access_token is not None,
        token_valid=is_valid,
        expires_at=(
            upstox_service._token_expiry.isoformat()
            if upstox_service._token_expiry
            else None
        ),
        user_profile=user_profile,
    )


@router.post("/logout")
async def upstox_logout():
    """
    Logout and revoke access token

    Clears the stored access token from the service.
    """
    upstox_service.revoke_token()
    return {"message": "Logged out successfully"}


@router.get("/profile", response_model=UpstoxUserProfile)
async def get_user_profile():
    """
    Get authenticated user's profile information

    Requires valid access token.
    """
    if not upstox_service.is_token_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login first.",
        )

    profile_data = await upstox_service.get_user_profile()

    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile",
        )

    return UpstoxUserProfile(**profile_data.get("data", {}))
