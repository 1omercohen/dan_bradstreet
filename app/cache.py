import redis.asyncio as redis
import json
import logging
from typing import Optional

from app.exceptions import CacheException

from app.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self._redis = None

    async def get_redis(self):
        if not self._redis:
            try:
                self._redis = redis.from_url(self.redis_url, decode_responses=True)
                await self._redis.ping()
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise CacheException(f"Redis connection failed: {str(e)}")
        return self._redis

    async def get(self, key: str) -> Optional[dict]:
        try:
            redis_client = await self.get_redis()
            cached_data = await redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except CacheException:
            raise
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            raise CacheException(f"Failed to get key {key}: {str(e)}")

    async def set(self, key: str, value: dict, ttl: int = None) -> bool:
        try:
            redis_client = await self.get_redis()
            if ttl:
                await redis_client.setex(key, ttl, json.dumps(value, default=str))
            else:
                await redis_client.set(key, json.dumps(value, default=str))
            return True
        except CacheException:
            raise
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            raise CacheException(f"Failed to set key {key}: {str(e)}")

    async def delete(self, key: str) -> bool:
        try:
            redis_client = await self.get_redis()
            await redis_client.delete(key)
            return True
        except CacheException:
            raise
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            raise CacheException(f"Failed to delete key {key}: {str(e)}")

    async def close(self):
        if self._redis:
            await self._redis.close()

cache_service = CacheService()