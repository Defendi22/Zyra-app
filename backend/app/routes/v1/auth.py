"""
Authentication Routes — Login, Register, Logout, Refresh Token, Profile
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends, Request

from app.models.user import (
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    UserResponse,
    UserProfileUpdate,
    RefreshTokenResponse,
)
from app.services.auth_service import auth_service
from app.services.user_service import user_service

logger = logging.getLogger("zyra.auth")

router = APIRouter()


# ==================== DEPENDENCIES ====================

def require_auth(request: Request) -> str:
    """Dependency to ensure user is authenticated"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


# ==================== ENDPOINTS ====================

@router.post("/register", response_model=AuthResponse, tags=["Auth"])
async def register(body: RegisterRequest):
    """
    Register new user with email, password, and username.

    Returns: access_token + user profile
    """
    try:
        # Validate input
        if len(body.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters",
            )

        if len(body.username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters",
            )

        # Call auth service
        result = await auth_service.register(
            email=body.email,
            password=body.password,
            username=body.username,
        )

        logger.info(f"User registered: {body.email}")
        return result

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Register validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Register error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=AuthResponse, tags=["Auth"])
async def login(body: LoginRequest):
    """
    Authenticate user with email and password.

    Returns: access_token + user profile
    """
    try:
        result = await auth_service.login(
            email=body.email,
            password=body.password,
        )

        logger.info(f"User logged in: {body.email}")
        return result

    except ValueError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/logout", tags=["Auth"])
async def logout(request: Request, user_id: str = Depends(require_auth)):
    """
    Logout user — invalidates token in Redis blacklist.

    Requires: Bearer token in Authorization header
    """
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header",
            )

        token = auth_header.replace("Bearer ", "")

        # Call auth service
        await auth_service.logout(user_id, token)

        logger.info(f"User logged out: {user_id}")
        return {
            "message": "Logged out successfully",
            "status": "ok",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )


@router.post("/refresh-token", response_model=RefreshTokenResponse, tags=["Auth"])
async def refresh_token(user_id: str = Depends(require_auth)):
    """
    Refresh access token (generates new JWT token).

    Requires: Valid Bearer token in Authorization header
    """
    try:
        result = await auth_service.refresh_token(user_id)
        logger.info(f"Token refreshed for user: {user_id}")
        return result

    except Exception as e:
        logger.error(f"Refresh token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.get("/me", response_model=UserResponse, tags=["Auth"])
async def get_current_user(user_id: str = Depends(require_auth)):
    """
    Get current authenticated user profile.

    Requires: Valid Bearer token in Authorization header
    """
    try:
        profile = await user_service.get_profile(user_id)
        logger.debug(f"Get profile for user: {user_id}")
        return profile

    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile",
        )


@router.patch("/me", response_model=UserResponse, tags=["Auth"])
async def update_current_user(
    body: UserProfileUpdate,
    user_id: str = Depends(require_auth),
):
    """
    Update current user profile.

    Requires: Valid Bearer token in Authorization header
    """
    try:
        profile = await user_service.update_profile(user_id, body)
        logger.info(f"Profile updated for user: {user_id}")
        return profile

    except Exception as e:
        logger.error(f"Update profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )
