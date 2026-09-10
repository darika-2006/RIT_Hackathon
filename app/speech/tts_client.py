import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class TtsClient:
    def __init__(self):
        self.enabled = settings.TTS_ENABLED
        self.base_url = settings.TTS_BASE_URL

    async def synthesize(self, text: str, language: str = "ta") -> Optional[str]:
        """
        Optional TTS synthesizer.
        Returns base64 encoded audio string if TTS is enabled and service responds, else None.
        """
        if not self.enabled:
            return None
        logger.info(f"TTS requested for text: '{text[:30]}...' in lang: {language}")
        # Placeholder for TTS microservice hook
        return None


tts_client = TtsClient()
