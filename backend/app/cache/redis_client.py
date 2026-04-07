"""
Cliente Upstash Redis (async)
Suporta conexão local para desenvolvimento
"""

import logging
from typing import Any, Optional
import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger("zyra.redis")


class AsyncRedisClient:
    """Wrapper async para Redis — Upstash em produção, local em dev"""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Conectar ao Redis"""
        try:
            self.client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf8",
                decode_responses=True,
            )
            # Testar conexão
            await self.ping()
            logger.info(f"✅ Redis conectado: {settings.REDIS_URL}")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise

    async def close(self):
        """Fechar conexão"""
        if self.client:
            await self.client.close()
            logger.info("👋 Redis desconectado")

    async def ping(self) -> bool:
        """Verificar conexão"""
        if not self.client:
            await self.connect()
        return await self.client.ping()

    # ==================== CACHE OPS ====================

    async def get(self, key: str) -> Optional[str]:
        """GET"""
        return await self.client.get(key)

    async def set(
        self, key: str, value: Any, ttl: int = None
    ) -> bool:
        """SET com TTL opcional"""
        ttl = ttl or settings.REDIS_CACHE_TTL
        result = await self.client.set(key, value, ex=ttl)
        return result

    async def delete(self, key: str) -> int:
        """DELETE"""
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """EXISTS"""
        return bool(await self.client.exists(key))

    # ==================== COUNTER OPS ====================

    async def incr(self, key: str) -> int:
        """INCR — incrementa e retorna novo valor"""
        return await self.client.incr(key)

    async def decr(self, key: str) -> int:
        """DECR"""
        return await self.client.decr(key)

    async def expire(self, key: str, seconds: int) -> bool:
        """EXPIRE — expirar chave em N segundos"""
        return bool(await self.client.expire(key, seconds))

    # ==================== HASH OPS ====================

    async def hset(self, key: str, field: str, value: Any) -> int:
        """HSET"""
        return await self.client.hset(key, field, value)

    async def hget(self, key: str, field: str) -> Optional[str]:
        """HGET"""
        return await self.client.hget(key, field)

    async def hgetall(self, key: str) -> dict:
        """HGETALL"""
        return await self.client.hgetall(key)

    # ==================== LIST OPS ====================

    async def lpush(self, key: str, value: Any) -> int:
        """LPUSH"""
        return await self.client.lpush(key, value)

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> list:
        """LRANGE"""
        return await self.client.lrange(key, start, end)

    # ==================== UTILITY ====================

    async def clear_by_pattern(self, pattern: str) -> int:
        """Deletar todas as chaves que matcham pattern"""
        cursor = 0
        count = 0
        while True:
            cursor, keys = await self.client.scan(cursor, match=pattern, count=100)
            if keys:
                count += await self.client.delete(*keys)
            if cursor == 0:
                break
        return count


# Instância global
redis_client = AsyncRedisClient()
