from typing import Any, Optional
from redis.asyncio import Redis
from .config import get_settings

class Cache:
    _instance = None
    _redis = None

    @classmethod
    async def get_instance(cls):
        """캐시 인스턴스를 가져옵니다.
        
        Returns:
            캐시 인스턴스
        """
        if not cls._instance:
            cls._instance = cls()
            settings = get_settings()
            cls._redis = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        return cls._instance

    async def get(self, key: str) -> Optional[str]:
        """키에 해당하는 값을 가져옵니다.
        
        Args:
            key: 캐시 키
            
        Returns:
            캐시 값, 없으면 None
        """
        return await self._redis.get(key)

    async def set(self, key: str, value: Any, expire: int = 3600):
        """키에 값을 설정하고 만료 시간을 설정합니다.
        
        Args:
            key: 캐시 키
            value: 캐시 값
            expire: 만료 시간 (기본값: 1시간)
        """
        await self._redis.set(key, value, ex=expire)

    async def delete(self, key: str):
        """키에 해당하는 값을 삭제합니다.
        
        Args:
            key: 캐시 키
        """
        await self._redis.delete(key) 