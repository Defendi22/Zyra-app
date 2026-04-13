"""
Roteador Social — Posts, Feed, Amizades, Likes, Comparação
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.middleware.auth import require_auth
from app.services.social_service import social_service

router = APIRouter()


# ==================== SCHEMAS ====================

class CreatePostRequest(BaseModel):
    type: str = Field(..., description="'workout' | 'diet' | 'achievement' | 'photo'")
    content: str = Field(..., min_length=1, max_length=2000)
    media_url: Optional[str] = None
    visibility: str = Field("public", description="'public' | 'friends' | 'private'")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "workout",
                "content": "Treino incrível hoje! 💪 60 minutos de peito e tríceps.",
                "media_url": None,
                "visibility": "public",
            }
        }


class PostResponse(BaseModel):
    id: str
    user_id: str
    type: str
    content: str
    media_url: Optional[str]
    visibility: str
    likes_count: int = 0
    created_at: str


class FriendRequestResponse(BaseModel):
    id: str
    requester_id: str
    addressee_id: str
    status: str
    created_at: str


class LikeResponse(BaseModel):
    post_id: str
    liked: bool
    likes_count: int


# ==================== POSTS ====================

@router.post("/posts", response_model=PostResponse, status_code=201)
async def create_post(
    body: CreatePostRequest,
    user_id: str = Depends(require_auth),
):
    """Criar novo post"""
    if body.type not in ("workout", "diet", "achievement", "photo"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo inválido. Use: workout, diet, achievement, photo",
        )
    if body.visibility not in ("public", "friends", "private"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Visibilidade inválida. Use: public, friends, private",
        )
    try:
        return await social_service.create_post(
            user_id=user_id,
            type=body.type,
            content=body.content,
            media_url=body.media_url,
            visibility=body.visibility,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: str,
    user_id: str = Depends(require_auth),
):
    """Deletar post (só o dono)"""
    deleted = await social_service.delete_post(post_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post não encontrado")


# ==================== FEED ====================

@router.get("/feed", response_model=List[PostResponse])
async def get_feed(
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(require_auth),
):
    """Feed personalizado — posts dos amigos + públicos"""
    try:
        return await social_service.get_feed(user_id=user_id, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/public-feed", response_model=List[PostResponse])
async def get_public_feed(
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    """Feed público — sem autenticação"""
    try:
        return await social_service.get_public_feed(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LIKES ====================

@router.post("/posts/{post_id}/like", response_model=LikeResponse)
async def like_post(
    post_id: str,
    user_id: str = Depends(require_auth),
):
    """Curtir um post"""
    try:
        return await social_service.like_post(post_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/posts/{post_id}/like", response_model=LikeResponse)
async def unlike_post(
    post_id: str,
    user_id: str = Depends(require_auth),
):
    """Descurtir um post"""
    try:
        return await social_service.unlike_post(post_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AMIZADES ====================

@router.post("/friendships/request/{addressee_id}", response_model=FriendRequestResponse, status_code=201)
async def send_friend_request(
    addressee_id: str,
    user_id: str = Depends(require_auth),
):
    """Enviar pedido de amizade"""
    try:
        return await social_service.send_friend_request(user_id, addressee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/friendships/accept/{request_id}", response_model=FriendRequestResponse)
async def accept_friend_request(
    request_id: str,
    user_id: str = Depends(require_auth),
):
    """Aceitar pedido de amizade"""
    try:
        return await social_service.accept_friend_request(request_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/friendships/pending")
async def get_pending_requests(
    user_id: str = Depends(require_auth),
):
    """Pedidos de amizade pendentes"""
    try:
        return await social_service.get_pending_requests(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/friends")
async def get_friends(
    user_id: str = Depends(require_auth),
):
    """Lista de amigos"""
    try:
        return await social_service.get_friends(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== COMPARAÇÃO ====================

@router.get("/compare/{friend_id}")
async def compare_metrics(
    friend_id: str,
    user_id: str = Depends(require_auth),
):
    """Comparar métricas de saúde com um amigo"""
    try:
        return await social_service.compare_metrics(user_id, friend_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))