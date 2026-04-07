"""
Authentication service — register, login, token management
"""

import jwt
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from passlib.context import CryptContext

from app.config import settings
from app.cache.redis_client import redis_client
from app.db.supabase_client import supabase_client
from app.models.user import UserResponse

logger = logging.getLogger("zyra.auth")

# ==================== PASSWORD HASHING ====================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt (max 72 bytes)"""
    # bcrypt has a 72-byte limit, truncate if needed
    password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # bcrypt has a 72-byte limit, truncate if needed
    plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


# ==================== AUTH SERVICE ====================

class AuthService:
    """Authentication service"""

    @staticmethod
    async def register(email: str, password: str, username: str) -> Dict:
        """
        Register new user.
        Returns: {"access_token", "token_type", "user_id", "user"}
        """
        try:
            logger.info(f"Registering user: {email}")

            # Hash password
            hashed_password = hash_password(password)

            # Try to create user in Supabase
            user_data = {
                "email": email,
                "username": username,
                "password_hash": hashed_password,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            try:
                result = supabase_client.insert_one("profiles", user_data)
                user_id = result.get("id")
                logger.info(f"User created in Supabase: {user_id}")
            except Exception as e:
                logger.warning(f"Supabase unavailable, using mock: {e}")
                # Mock user creation in dev
                user_id = f"mock_{username[:8]}_{int(time.time())}"

            # Generate JWT token
            token = AuthService._generate_token(user_id)

            # Create user response
            user_response = UserResponse(
                id=user_id,
                email=email,
                username=username,
                bio=None,
                avatar_url=None,
                created_at=datetime.utcnow(),
            )

            return {
                "access_token": token,
                "token_type": "bearer",
                "user_id": user_id,
                "user": user_response,
            }

        except Exception as e:
            logger.error(f"Register failed: {e}")
            raise

    @staticmethod
    async def login(email: str, password: str) -> Dict:
        """
        Authenticate user.
        Returns: {"access_token", "token_type", "user_id", "user"}
        """
        try:
            logger.info(f"Login attempt: {email}")

            # Try to fetch user from Supabase
            try:
                user_data = supabase_client.select_all(
                    "profiles",
                    filters={"email": email},
                    limit=1,
                )
                if not user_data:
                    logger.warning(f"User not found: {email}")
                    raise ValueError("Invalid email or password")

                user = user_data[0]
                user_id = user.get("id")

                # Verify password
                stored_hash = user.get("password_hash")
                if not verify_password(password, stored_hash):
                    logger.warning(f"Wrong password for {email}")
                    raise ValueError("Invalid email or password")

            except Exception as e:
                if isinstance(e, ValueError):
                    raise
                logger.warning(f"Supabase unavailable, using mock: {e}")
                # Mock login in dev - accept any password
                user_id = f"mock_{email.split('@')[0]}_{int(time.time())}"
                user = {
                    "id": user_id,
                    "email": email,
                    "username": email.split("@")[0],
                    "bio": None,
                    "avatar_url": None,
                    "created_at": datetime.utcnow().isoformat(),
                }

            # Generate JWT token
            token = AuthService._generate_token(user_id)

            # Create user response
            user_response = UserResponse(
                id=user.get("id"),
                email=user.get("email"),
                username=user.get("username", email.split("@")[0]),
                bio=user.get("bio"),
                avatar_url=user.get("avatar_url"),
                created_at=(
                    datetime.fromisoformat(user.get("created_at"))
                    if isinstance(user.get("created_at"), str)
                    else user.get("created_at", datetime.utcnow())
                ),
            )

            logger.info(f"User logged in: {user_id}")

            return {
                "access_token": token,
                "token_type": "bearer",
                "user_id": user_id,
                "user": user_response,
            }

        except ValueError as e:
            logger.warning(f"Login failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise

    @staticmethod
    async def logout(user_id: str, token: str) -> bool:
        """
        Logout user — add token to Redis blacklist.
        Token will be invalid for the remaining TTL.
        """
        try:
            # Decode token to get expiration
            decoded = jwt.decode(
                token,
                settings.SUPABASE_ANON_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            exp = decoded.get("exp", 0)
            ttl_seconds = max(exp - int(time.time()), 1)

            # Add token to blacklist
            blacklist_key = f"token_blacklist:{token}"
            await redis_client.set(blacklist_key, user_id, ttl=ttl_seconds)

            logger.info(f"User logged out: {user_id}")
            return True

        except Exception as e:
            logger.warning(f"Logout failed (non-critical): {e}")
            # Don't fail logout on error
            return False

    @staticmethod
    async def refresh_token(user_id: str) -> Dict:
        """
        Refresh access token (requires valid token).
        Returns: {"access_token", "token_type"}
        """
        try:
            # Generate new JWT token
            token = AuthService._generate_token(user_id)

            logger.info(f"Token refreshed for user: {user_id}")

            return {
                "access_token": token,
                "token_type": "bearer",
            }

        except Exception as e:
            logger.error(f"Refresh token failed: {e}")
            raise

    @staticmethod
    def _generate_token(user_id: str, expires_hours: int = None) -> str:
        """
        Generate JWT token for user.
        Uses Supabase ANON_KEY as signing key (HS256).
        """
        expires_hours = expires_hours or settings.JWT_EXPIRATION_HOURS

        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_hours),
        }

        token = jwt.encode(
            payload,
            settings.SUPABASE_ANON_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        return token

    @staticmethod
    def verify_token_signature(token: str) -> Optional[str]:
        """
        Verify token signature and return user_id.
        Used for token validation.
        """
        try:
            decoded = jwt.decode(
                token,
                settings.SUPABASE_ANON_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return decoded.get("sub")
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise
        except jwt.DecodeError:
            logger.warning("Invalid token signature")
            raise


# ==================== SINGLETON ====================

auth_service = AuthService()
