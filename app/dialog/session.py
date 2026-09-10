import json
import logging
from typing import Optional, Dict, Any
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.ttl = settings.SESSION_TTL_SECONDS
        self._redis_client: Optional[redis.Redis] = None
        self._memory_store: Dict[str, str] = {}
        self._redis_failed = False

    async def get_client(self) -> Optional[redis.Redis]:
        if self._redis_failed:
            return None
        if self._redis_client is None:
            try:
                client = redis.from_url(self.redis_url, socket_timeout=1.0)
                await client.ping()
                self._redis_client = client
                logger.info("Connected to Redis Session Store.")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using memory session store fallback.")
                self._redis_failed = True
                self._redis_client = None
        return self._redis_client

    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieves session data by session_id"""
        client = await self.get_client()
        if client:
            try:
                data = await client.get(f"session:{session_id}")
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}. Falling back to memory store.")
                self._redis_failed = True
                self._redis_client = None

        raw = self._memory_store.get(session_id)
        if raw:
            return json.loads(raw)

        return {
            "session_id": session_id,
            "dialog_state": "GREETING",
            "current_intent": None,
            "slots": {},
            "history": []
        }

    async def save_session(self, session_id: str, state: Dict[str, Any]) -> None:
        """Saves session data with 30m TTL"""
        payload = json.dumps(state)
        # Always update local memory store for instant fallback consistency
        self._memory_store[session_id] = payload

        client = await self.get_client()
        if client:
            try:
                await client.set(f"session:{session_id}", payload, ex=self.ttl)
            except Exception as e:
                logger.warning(f"Redis set failed: {e}. Retaining memory store.")
                self._redis_failed = True
                self._redis_client = None

    async def clear_session(self, session_id: str) -> None:
        """Clears session data"""
        self._memory_store.pop(session_id, None)
        client = await self.get_client()
        if client:
            try:
                await client.delete(f"session:{session_id}")
            except Exception:
                pass


session_manager = SessionManager()
