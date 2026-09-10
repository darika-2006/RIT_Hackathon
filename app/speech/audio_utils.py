import logging
from typing import Tuple

logger = logging.getLogger(__name__)

MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {
    "wav": "audio/wav",
    "webm": "audio/webm",
    "ogg": "audio/ogg",
    "mp3": "audio/mp3",
    "m4a": "audio/m4a",
    "flac": "audio/flac"
}


class AudioValidationError(Exception):
    """Exception raised when audio payload validation fails"""
    pass


def validate_and_normalize_audio(
    audio_bytes: bytes,
    filename: str = "audio.webm",
    content_type: str = None
) -> Tuple[bytes, str, str]:
    """
    Validates audio byte stream and normalizes filename & content_type.
    Returns (audio_bytes, sanitized_filename, sanitized_content_type).
    Raises AudioValidationError if validation fails.
    """
    if not audio_bytes or len(audio_bytes) == 0:
        raise AudioValidationError("Empty audio payload received")

    if len(audio_bytes) > MAX_AUDIO_SIZE_BYTES:
        size_mb = len(audio_bytes) / (1024 * 1024)
        raise AudioValidationError(f"Audio payload size ({size_mb:.2f}MB) exceeds 10MB limit")

    ext = "webm"
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()

    resolved_content_type = content_type
    if not resolved_content_type or resolved_content_type == "application/octet-stream":
        resolved_content_type = ALLOWED_EXTENSIONS.get(ext, "audio/webm")

    sanitized_filename = filename if filename else f"audio.{ext}"
    return audio_bytes, sanitized_filename, resolved_content_type
