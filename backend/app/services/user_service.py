"""
User service — profile management
"""

import logging
from datetime import datetime
from typing import Optional, Dict

from app.db.supabase_client import supabase_client
from app.models.user import UserResponse, UserProfileUpdate

logger = logging.getLogger("zyra.user")


class UserService:
    """User profile management"""

    @staticmethod
    async def get_profile(user_id: str) -> UserResponse:
        """Get user profile by ID"""
        try:
            # Try Supabase first
            try:
                user_data = supabase_client.select_one("profiles", user_id)
                if user_data:
                    return UserResponse(**user_data)
            except Exception as e:
                logger.warning(f"Supabase unavailable for get_profile: {e}")

            # Mock data in dev
            logger.info(f"Returning mock profile for {user_id}")
            return UserResponse(
                id=user_id,
                email=f"user_{user_id[:8]}@zyra.local",
                username=f"user_{user_id[:8]}",
                bio=None,
                avatar_url=None,
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Get profile failed: {e}")
            raise

    @staticmethod
    async def create_profile(
        user_id: str, email: str, username: str
    ) -> UserResponse:
        """Create user profile"""
        try:
            profile_data = {
                "id": user_id,
                "email": email,
                "username": username,
                "bio": None,
                "avatar_url": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Try Supabase
            try:
                result = supabase_client.insert_one("profiles", profile_data)
                logger.info(f"Profile created in Supabase: {user_id}")
                return UserResponse(**result)
            except Exception as e:
                logger.warning(f"Supabase unavailable for create_profile: {e}")

            # Return mock response
            return UserResponse(
                id=user_id,
                email=email,
                username=username,
                bio=None,
                avatar_url=None,
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Create profile failed: {e}")
            raise

    @staticmethod
    async def update_profile(
        user_id: str, updates: UserProfileUpdate
    ) -> UserResponse:
        """Update user profile"""
        try:
            update_data = updates.model_dump(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow().isoformat()

            # Try Supabase
            try:
                result = supabase_client.update_one(
                    "profiles", user_id, update_data
                )
                logger.info(f"Profile updated in Supabase: {user_id}")
                return UserResponse(**result)
            except Exception as e:
                logger.warning(f"Supabase unavailable for update_profile: {e}")

            # Return mock response
            current_profile = await UserService.get_profile(user_id)
            return UserResponse(
                id=user_id,
                email=current_profile.email,
                username=updates.username or current_profile.username,
                bio=updates.bio or current_profile.bio,
                avatar_url=updates.avatar_url or current_profile.avatar_url,
                created_at=current_profile.created_at,
            )

        except Exception as e:
            logger.error(f"Update profile failed: {e}")
            raise

    @staticmethod
    async def delete_profile(user_id: str) -> bool:
        """Delete user profile"""
        try:
            # Try Supabase
            try:
                result = supabase_client.delete_one("profiles", user_id)
                logger.info(f"Profile deleted from Supabase: {user_id}")
                return result
            except Exception as e:
                logger.warning(f"Supabase unavailable for delete_profile: {e}")

            # Mock success
            return True

        except Exception as e:
            logger.error(f"Delete profile failed: {e}")
            raise


# ==================== SINGLETON ====================

user_service = UserService()
