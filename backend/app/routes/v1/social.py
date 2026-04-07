"""
Roteador Social — Posts, Amizades, Feed, Comparação de Métricas
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.middleware.auth import require_auth

router = APIRouter()

# ==================== SCHEMAS ====================

class CreatePostRequest(BaseModel):
    """Criar novo post"""
    type: str  # 'workout' | 'diet' | 'achievement' | 'photo'
    content: str
    media_url: Optional[str] = None
    visibility: str = "public"  # 'public' | 'friends' | 'private'


class PostResponse(BaseModel):
    """Response de post"""
    id: str
    user_id: str
    type: str
    content: str
    media_url: Optional[str]
    visibility: str
    created_at: datetime
    likes_count: int = 0


class FriendRequestResponse(BaseModel):
    """Response de amizade"""
    id: str
    requester_id: str
    addressee_id: str
    status: str  # 'pending' | 'accepted'
    created_at: datetime


# ==================== ENDPOINTS ====================

@router.post("/posts", response_model=PostResponse)
async def create_post(
    request: Request,
    body: CreatePostRequest,
    user_id: str = Depends(require_auth),
):
    """Criar novo post"""
    # TODO: Implementar criação de post
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.get("/feed", response_model=List[PostResponse])
async def get_feed(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    user_id: str = Depends(require_auth),
):
    """Obter feed personalizado (amigos em destaque)"""
    # TODO: Implementar feed
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.get("/public-feed", response_model=List[PostResponse])
async def get_public_feed(limit: int = 20, offset: int = 0):
    """Obter feed público cronológico (sem autenticação)"""
    # TODO: Implementar feed público
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.post("/friendships/request/{friend_id}")
async def send_friend_request(
    request: Request,
    friend_id: str,
    user_id: str = Depends(require_auth),
):
    """Enviar pedido de amizade"""
    # TODO: Implementar pedido de amizade
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.post("/friendships/accept/{request_id}")
async def accept_friend_request(
    request: Request,
    request_id: str,
    user_id: str = Depends(require_auth),
):
    """Aceitar pedido de amizade"""
    # TODO: Implementar aceitação de pedido
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.get("/friends")
async def get_friends(
    request: Request,
    user_id: str = Depends(require_auth),
):
    """Listar amigos"""
    # TODO: Implementar lista de amigos
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.get("/compare/{friend_id}")
async def compare_metrics(
    request: Request,
    friend_id: str,
    user_id: str = Depends(require_auth),
):
    """Comparar métricas com amigo"""
    # TODO: Implementar comparação de métricas
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )
