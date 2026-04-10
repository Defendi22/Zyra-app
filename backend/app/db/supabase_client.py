"""
Cliente Supabase — Postgres + Auth + Storage
"""

import logging
from typing import Optional, List, Dict, Any
from supabase import create_client, Client

from app.config import settings

logger = logging.getLogger("zyra.db")


class SupabaseClient:
    """Wrapper para Supabase — Postgres + Auth + Storage (R2 via API)"""

    def __init__(self):
        self.client: Optional[Client] = None
        self.service_client: Optional[Client] = None

    def connect(self):
        """Conectar ao Supabase"""
        try:
            # Cliente anon (para operações de usuários normais)
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY,
            )

            # Cliente com service role (para operações administrativas)
            self.service_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY,
            )

            logger.info(f"✅ Supabase conectado: {settings.SUPABASE_URL}")
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
            raise

    def health_check(self) -> bool:
        """Verificar saúde da conexão"""
        try:
            # Tentar query simples
            response = self.client.table("profiles").select("count", count="exact").limit(1).execute()
            logger.info("✅ Supabase health check OK")
            return True
        except Exception as e:
            logger.error(f"❌ Supabase health check failed: {e}")
            raise

    # ==================== QUERIES ====================

    def query(self, table: str):
        """Retorna um builder para queries — encadeia .select().where().execute()"""
        return self.client.table(table)

    def admin_query(self, table: str):
        """Query com service role (bypass RLS)"""
        return self.service_client.table(table)

    # ==================== INSERT ====================

    def insert_one(self, table: str, data: dict) -> dict:
        """INSERT um registro — usa service role para bypass RLS"""
        response = self.service_client.table(table).insert([data]).execute()
        return response.data[0] if response.data else None

    def insert_many(self, table: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """INSERT múltiplos registros"""
        response = self.client.table(table).insert(data).execute()
        return response.data

    # ==================== SELECT ====================

    def select_one(self, table: str, id: str, column: str = "id") -> Optional[Dict[str, Any]]:
        """SELECT um registro por ID"""
        response = (
            self.client.table(table)
            .select("*")
            .eq(column, id)
            .single()
            .execute()
        )
        return response.data

    def select_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """SELECT múltiplos registros com filtros opcionais"""
        query = self.client.table(table).select("*")

        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)

        response = query.range(offset, offset + limit - 1).execute()
        return response.data

    # ==================== UPDATE ====================

    def update_one(self, table: str, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """UPDATE um registro"""
        response = (
            self.client.table(table)
            .update(data)
            .eq("id", id)
            .execute()
        )
        return response.data[0] if response.data else None

    # ==================== DELETE ====================

    def delete_one(self, table: str, id: str) -> bool:
        """DELETE um registro"""
        response = self.client.table(table).delete().eq("id", id).execute()
        return len(response.data) > 0

    # ==================== STORAGE ====================

    def upload_file(self, bucket: str, path: str, file_data: bytes) -> str:
        """Upload arquivo para Supabase Storage"""
        try:
            response = self.client.storage.from_(bucket).upload(path, file_data)
            logger.info(f"✅ File uploaded: {bucket}/{path}")
            return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"
        except Exception as e:
            logger.error(f"❌ File upload failed: {e}")
            raise

    def delete_file(self, bucket: str, path: str) -> bool:
        """Deletar arquivo do Supabase Storage"""
        try:
            self.client.storage.from_(bucket).remove([path])
            logger.info(f"✅ File deleted: {bucket}/{path}")
            return True
        except Exception as e:
            logger.error(f"❌ File deletion failed: {e}")
            return False

    # ==================== RLS HELPERS ====================

    def set_session(self, access_token: str):
        """Setar access token para RLS (executa como usuário específico)"""
        self.client.auth.set_session(access_token, refresh_token=None)

    # ==================== ADMIN OPS ====================

    def admin_get_user(self, user_id: str) -> Dict[str, Any]:
        """Get usuário por ID (admin only)"""
        return self.service_client.auth.admin.get_user(user_id)

    def admin_create_user(
        self, email: str, password: str, user_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Criar usuário (admin only) — deprecated, use Supabase Auth UI"""
        return self.service_client.auth.admin.create_user(
            email=email,
            password=password,
            user_metadata=user_metadata,
        )


# Instância global
supabase_client = SupabaseClient()
