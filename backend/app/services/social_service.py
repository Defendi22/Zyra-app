"""
Social Service — Posts, Feed, Amizades, Likes
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict
from uuid import uuid4

from app.db.supabase_client import supabase_client

logger = logging.getLogger("zyra.social")


class SocialService:

    # ==================== POSTS ====================

    @staticmethod
    async def create_post(
        user_id: str,
        type: str,
        content: str,
        media_url: Optional[str] = None,
        visibility: str = "public",
    ) -> Dict:
        """Cria um novo post"""
        data = {
            "user_id": user_id,
            "type": type,
            "content": content,
            "media_url": media_url,
            "visibility": visibility,
            "likes_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            result = supabase_client.service_client.table("posts").insert(data).execute()
            record = result.data[0] if result.data else {"id": str(uuid4()), **data}
            logger.info(f"Post criado por {user_id}: type={type}")
            return record
        except Exception as e:
            logger.warning(f"Erro ao criar post: {e}")
            return {"id": str(uuid4()), **data}

    @staticmethod
    async def get_public_feed(limit: int = 20, offset: int = 0) -> List[Dict]:
        """Feed público — posts públicos mais recentes"""
        try:
            result = (
                supabase_client.service_client
                .table("posts")
                .select("*, profiles(username, avatar_url)")
                .eq("visibility", "public")
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.warning(f"Erro ao buscar feed público: {e}")
            return []

    @staticmethod
    async def get_feed(user_id: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """
        Feed personalizado — posts dos amigos primeiro, depois públicos.
        """
        try:
            # Busca IDs dos amigos
            friend_ids = await SocialService._get_friend_ids(user_id)

            if friend_ids:
                # Posts dos amigos
                result = (
                    supabase_client.service_client
                    .table("posts")
                    .select("*, profiles(username, avatar_url)")
                    .in_("user_id", friend_ids)
                    .in_("visibility", ["public", "friends"])
                    .order("created_at", desc=True)
                    .range(offset, offset + limit - 1)
                    .execute()
                )
                posts = result.data or []
            else:
                posts = []

            # Completa com posts públicos se necessário
            if len(posts) < limit:
                remaining = limit - len(posts)
                public_result = (
                    supabase_client.service_client
                    .table("posts")
                    .select("*, profiles(username, avatar_url)")
                    .eq("visibility", "public")
                    .order("created_at", desc=True)
                    .limit(remaining)
                    .execute()
                )
                public_posts = public_result.data or []
                # Evita duplicatas
                existing_ids = {p["id"] for p in posts}
                posts += [p for p in public_posts if p["id"] not in existing_ids]

            return posts
        except Exception as e:
            logger.warning(f"Erro ao buscar feed: {e}")
            return []

    @staticmethod
    async def delete_post(post_id: str, user_id: str) -> bool:
        """Deleta post — só o dono pode deletar"""
        try:
            result = (
                supabase_client.service_client
                .table("posts")
                .delete()
                .eq("id", post_id)
                .eq("user_id", user_id)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            logger.warning(f"Erro ao deletar post: {e}")
            return False

    # ==================== LIKES ====================

    @staticmethod
    async def like_post(post_id: str, user_id: str) -> Dict:
        """Curtir um post"""
        try:
            # Insere o like
            supabase_client.service_client.table("post_likes").insert({
                "post_id": post_id,
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()

            # Incrementa contador
            result = (
                supabase_client.service_client
                .table("posts")
                .select("likes_count")
                .eq("id", post_id)
                .single()
                .execute()
            )
            current = result.data.get("likes_count", 0) if result.data else 0
            supabase_client.service_client.table("posts").update(
                {"likes_count": current + 1}
            ).eq("id", post_id).execute()

            return {"post_id": post_id, "liked": True, "likes_count": current + 1}
        except Exception as e:
            logger.warning(f"Erro ao curtir post: {e}")
            raise

    @staticmethod
    async def unlike_post(post_id: str, user_id: str) -> Dict:
        """Descurtir um post"""
        try:
            supabase_client.service_client.table("post_likes").delete().eq(
                "post_id", post_id
            ).eq("user_id", user_id).execute()

            result = (
                supabase_client.service_client
                .table("posts")
                .select("likes_count")
                .eq("id", post_id)
                .single()
                .execute()
            )
            current = result.data.get("likes_count", 0) if result.data else 0
            new_count = max(0, current - 1)
            supabase_client.service_client.table("posts").update(
                {"likes_count": new_count}
            ).eq("id", post_id).execute()

            return {"post_id": post_id, "liked": False, "likes_count": new_count}
        except Exception as e:
            logger.warning(f"Erro ao descurtir post: {e}")
            raise

    # ==================== AMIZADES ====================

    @staticmethod
    async def send_friend_request(requester_id: str, addressee_id: str) -> Dict:
        """Envia pedido de amizade"""
        if requester_id == addressee_id:
            raise ValueError("Não é possível adicionar a si mesmo")

        data = {
            "requester_id": requester_id,
            "addressee_id": addressee_id,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            result = supabase_client.service_client.table("friendships").insert(data).execute()
            record = result.data[0] if result.data else {"id": str(uuid4()), **data}
            logger.info(f"Pedido de amizade: {requester_id} → {addressee_id}")
            return record
        except Exception as e:
            logger.warning(f"Erro ao enviar pedido de amizade: {e}")
            raise

    @staticmethod
    async def accept_friend_request(request_id: str, user_id: str) -> Dict:
        """Aceita pedido de amizade — só o destinatário pode aceitar"""
        try:
            result = (
                supabase_client.service_client
                .table("friendships")
                .update({"status": "accepted"})
                .eq("id", request_id)
                .eq("addressee_id", user_id)
                .execute()
            )
            if not result.data:
                raise ValueError("Pedido não encontrado ou sem permissão")
            logger.info(f"Amizade aceita: {request_id}")
            return result.data[0]
        except Exception as e:
            logger.warning(f"Erro ao aceitar pedido: {e}")
            raise

    @staticmethod
    async def get_friends(user_id: str) -> List[Dict]:
        """Lista amigos aceitos"""
        try:
            result = (
                supabase_client.service_client
                .table("friendships")
                .select("*, requester:requester_id(id, username, avatar_url), addressee:addressee_id(id, username, avatar_url)")
                .eq("status", "accepted")
                .or_(f"requester_id.eq.{user_id},addressee_id.eq.{user_id}")
                .execute()
            )
            friends = []
            for f in (result.data or []):
                # Retorna o perfil do outro usuário
                if f["requester_id"] == user_id:
                    friends.append(f["addressee"])
                else:
                    friends.append(f["requester"])
            return friends
        except Exception as e:
            logger.warning(f"Erro ao buscar amigos: {e}")
            return []

    @staticmethod
    async def get_pending_requests(user_id: str) -> List[Dict]:
        """Lista pedidos de amizade pendentes recebidos"""
        try:
            result = (
                supabase_client.service_client
                .table("friendships")
                .select("*, requester:requester_id(id, username, avatar_url)")
                .eq("addressee_id", user_id)
                .eq("status", "pending")
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.warning(f"Erro ao buscar pedidos pendentes: {e}")
            return []

    # ==================== COMPARAÇÃO ====================

    @staticmethod
    async def compare_metrics(user_id: str, friend_id: str) -> Dict:
        """Compara últimas métricas de saúde entre dois usuários"""
        try:
            def get_latest(uid):
                result = (
                    supabase_client.service_client
                    .table("health_metrics")
                    .select("weight_kg, imc, tmb, date")
                    .eq("user_id", uid)
                    .order("date", desc=True)
                    .limit(1)
                    .execute()
                )
                return result.data[0] if result.data else None

            user_metrics = get_latest(user_id)
            friend_metrics = get_latest(friend_id)

            return {
                "user": user_metrics,
                "friend": friend_metrics,
            }
        except Exception as e:
            logger.warning(f"Erro ao comparar métricas: {e}")
            return {"user": None, "friend": None}

    # ==================== HELPERS ====================

    @staticmethod
    async def _get_friend_ids(user_id: str) -> List[str]:
        """Retorna lista de IDs dos amigos aceitos"""
        try:
            result = (
                supabase_client.service_client
                .table("friendships")
                .select("requester_id, addressee_id")
                .eq("status", "accepted")
                .or_(f"requester_id.eq.{user_id},addressee_id.eq.{user_id}")
                .execute()
            )
            ids = []
            for f in (result.data or []):
                if f["requester_id"] == user_id:
                    ids.append(f["addressee_id"])
                else:
                    ids.append(f["requester_id"])
            return ids
        except Exception as e:
            logger.warning(f"Erro ao buscar IDs de amigos: {e}")
            return []


social_service = SocialService()