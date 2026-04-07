"""
User models and schemas for auth + profile
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ==================== AUTH REQUESTS ====================

class LoginRequest(BaseModel):
    """User login"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """User registration"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    username: str = Field(..., min_length=3, max_length=30)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@zyra.com",
                "password": "SecurePassword123!",
                "username": "johndoe",
            }
        }


# ==================== AUTH RESPONSES ====================

class UserResponse(BaseModel):
    """User profile response"""
    id: str
    email: str
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Auth response with token"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    user: UserResponse

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGc...",
                "token_type": "bearer",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@zyra.com",
                    "username": "johndoe",
                    "bio": None,
                    "avatar_url": None,
                    "created_at": "2026-04-07T16:00:00",
                },
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    token_type: str = "bearer"


# ==================== PROFILE UPDATES ====================

class UserProfileUpdate(BaseModel):
    """Update user profile"""
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "newusername",
                "bio": "Fitness enthusiast 💪",
                "avatar_url": "https://cdn.zyra.com/avatars/user123.jpg",
            }
        }


# ==================== DATABASE MODELS ====================

class UserDB(BaseModel):
    """Database user model"""
    id: str
    email: str
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
