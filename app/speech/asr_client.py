import logging
from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.speech.audio_utils import validate_and_normalize_audio

logger = logging.getLogger(__name__)


class AsrError(Exception):
    """Custom exception raised when ASR transcription fails"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class AsrClient:
    def __init__(self):
        self.mode = settings.ASR_MODE.lower()
        self.base_url = settings.ASR_BASE_URL.rstrip('/')
        self.timeout = settings.ASR_TIMEOUT_SECONDS
        self.endpoint_path = settings.ASR_ENDPOINT_PATH.rstrip('/')

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        content_type: str = "audio/webm",
        language_hint: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes audio bytes to text using either HTTP ASR microservice or local ASR engine.
        Returns normalized dictionary shape:
        {
            "text": str,
            "confidence": float,
            "language": str,
            "raw": dict,
            "source": "http_asr" | "local_asr"
        }
        """
        # 1. Validate audio payload
        clean_bytes, clean_filename, clean_content_type = validate_and_normalize_audio(
            audio_bytes=audio_bytes,
            filename=filename,
            content_type=content_type
        )

        resolved_lang = language_hint if language_hint else settings.DEFAULT_LANGUAGE

        if self.mode == "local":
            return await self._transcribe_local(
                clean_bytes, clean_filename, clean_content_type, resolved_lang, session_id
            )
        else:
            return await self._transcribe_http(
                clean_bytes, clean_filename, clean_content_type, resolved_lang, session_id
            )

    async def _transcribe_http(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        language: str,
        session_id: Optional[str]
    ) -> Dict[str, Any]:
        """Sends multipart upload to ASR microservice running on Port 8002"""
        url = f"{self.base_url}{self.endpoint_path}"
        logger.info(f"Sending audio to HTTP ASR endpoint: {url}")

        files = {
            "file": (filename, audio_bytes, content_type)
        }
        # The configured ASR service is the Whisper/Groq microservice. Its model
        # is selected server-side, so do not send the remote Qwen LLM model here.
        data = {"language": language}
        if session_id:
            data["session_id"] = session_id

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, files=files, data=data)
                if resp.status_code == 200:
                    payload = resp.json()
                    text = (payload.get("text") or payload.get("transcript") or "").strip()
                    conf = payload.get("confidence", payload.get("avg_logprob", 0.90))
                    lang = payload.get("language", language)
                    return {
                        "text": text,
                        "confidence": float(conf) if conf is not None else 0.90,
                        "language": lang,
                        "raw": payload,
                        "source": "http_asr"
                    }
                else:
                    detail = f"ASR server returned HTTP {resp.status_code}: {resp.text}"
                    logger.error(detail)
                    raise AsrError(detail)
        except httpx.RequestError as req_err:
            detail = f"Unable to connect to ASR microservice at {url}: {req_err}"
            logger.error(detail)
            raise AsrError(detail, original_error=req_err)
        except AsrError:
            raise
        except Exception as e:
            detail = f"Unexpected error during ASR transcription: {e}"
            logger.error(detail)
            raise AsrError(detail, original_error=e)

    async def _transcribe_local(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        language: str,
        session_id: Optional[str]
    ) -> Dict[str, Any]:
        """Calls in-process asr_server module if configured for local mode"""
        try:
            from fastapi import UploadFile
            import io
            from asr_server import transcribe as local_transcribe

            upload_file = UploadFile(
                filename=filename,
                file=io.BytesIO(audio_bytes),
                headers={"content-type": content_type}
            )
            res = await local_transcribe(file=upload_file, language=language, session_id=session_id)
            res_dict = res.model_dump()
            return {
                "text": res_dict.get("text", "").strip(),
                "confidence": res_dict.get("confidence", 0.90),
                "language": res_dict.get("language", language),
                "raw": res_dict,
                "source": "local_asr"
            }
        except Exception as e:
            detail = f"Local in-process ASR failed: {e}"
            logger.error(detail)
            raise AsrError(detail, original_error=e)


asr_client = AsrClient()
