# asr_server.py - Universal Multilingual ASR Engine (Python 3.13/3.14 Compatible)
from dotenv import load_dotenv
load_dotenv()  # Always read GROQ_API_KEY (and others) from .env

import os
import io
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Universal-ASR")

app = FastAPI(
    title="Universal Vernacular ASR Engine",
    description="ASR Engine for Indian Micro-Banking",
    version="1.0.0"
)

# Enable CORS for Frontend/Client Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# 🔑 API KEY CONFIGURATION
# =====================================================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
ASR_HOST = os.environ.get("ASR_HOST", "0.0.0.0")
ASR_PORT = int(os.environ.get("ASR_PORT", "8002"))

# =====================================================================
# 1. CANONICAL OUTPUT SCHEMA CONTRACT
# =====================================================================
class ASRResponseSchema(BaseModel):
    session_id: str = Field(..., example="c9bf9e57-1685-4c89-bafb-ff5af830be8a")
    text: str = Field(..., example="मुझे loan चाहिए")
    confidence: float = Field(..., example=0.92)
    language: str = Field(..., example="hi")
    audio_duration_ms: int = Field(..., example=2300)
    timestamp: str = Field(..., example="2025-01-15T14:22:05.812941+00:00")

# =====================================================================
# 2. INITIALIZE GROQ API CLIENT
# =====================================================================
groq_client = None

if GROQ_API_KEY and GROQ_API_KEY != "YOUR_GROQ_API_KEY_HERE":
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("✅ Universal Groq Cloud API Initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Groq Client: {e}")
else:
    logger.warning("⚠️ GROQ_API_KEY is missing. Please set GROQ_API_KEY in environment or asr_server.py.")

UNIVERSAL_BANKING_PROMPT = (
    "Jan Dhan, Mudra loan, KCC, Kisan Credit Card, Self Help Group, SHG, "
    "Balance check, Mini statement, Deposit, Passbook, Account, DBT, "
    "₹500, ₹2000, ₹10000"
)

SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "en": "English",
    "te": "Telugu",
    "ta": "Tamil",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "as": "Assamese",
    "ur": "Urdu",
    "sa": "Sanskrit",
    "ne": "Nepali"
}

# Mapping common language names to ISO 639-1 codes
LANGUAGE_NAME_MAP = {
    "tamil": "ta",
    "telugu": "te",
    "hindi": "hi",
    "bengali": "bn",
    "marathi": "mr",
    "gujarati": "gu",
    "kannada": "kn",
    "malayalam": "ml",
    "punjabi": "pa",
    "assamese": "as",
    "urdu": "ur",
    "sanskrit": "sa",
    "nepali": "ne",
    "english": "en"
}

# Aliases for code-mixed languages
LANGUAGE_ALIASES = {
    "hinglish": "hi",
    "tunglish": "te",
    "tanglish": "ta",
    "kanglish": "kn"
}

# Swagger UI / placeholder values that should trigger automatic detection
AUTO_DETECT_KEYWORDS = {
    "auto", "detect", "string", "none", "null", "undefined", ""
}

# Valid 99 ISO language codes recognized by Whisper
VALID_WHISPER_LANGUAGES = {
    "af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs",
    "cy", "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu",
    "ha", "haw", "he", "hi", "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "jv", "ka",
    "kk", "km", "kn", "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml",
    "mn", "mr", "ms", "mt", "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt",
    "ro", "ru", "sa", "sd", "si", "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw",
    "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "uk", "ur", "uz", "vi", "yi", "yo",
    "yue", "zh"
}

# =====================================================================
# 3. HELPER & STATUS ENDPOINTS
# =====================================================================
@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Vernacular ASR Engine",
        "documentation": "/docs",
        "transcribe_endpoint": "/api/v1/transcribe",
        "languages_endpoint": "/api/v1/languages"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "groq_api_configured": groq_client is not None
    }

@app.get("/api/v1/languages")
def list_languages():
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
        "code_mixed_aliases": LANGUAGE_ALIASES,
        "language_name_map": LANGUAGE_NAME_MAP,
        "note": "Odia ('or') is not supported by Whisper. Leave blank or use 'auto' for automatic language detection."
    }

# =====================================================================
# 4. UNIVERSAL TRANSCRIBE ENDPOINT
# =====================================================================
@app.post("/api/v1/transcribe", response_model=ASRResponseSchema)
async def transcribe(
    file: UploadFile = File(...),
    language: Optional[str] = Form(
        None,
        description="Language code (e.g. 'ta' for Tamil, 'hi', 'te', 'en'), full name ('tamil'), or code-mixed alias ('tanglish', 'hinglish'). Leave blank or 'auto' for automatic detection."
    ),
    session_id: Optional[str] = Form(
        None,
        description="Optional session tracking ID. Leave blank to generate automatically."
    )
):
    # Sanitize session_id (ignore Swagger placeholder 'string')
    if session_id and session_id.strip().lower() not in AUTO_DETECT_KEYWORDS:
        active_session_id = session_id.strip()
    else:
        active_session_id = str(uuid.uuid4())
    
    raw_bytes = await file.read()
    if len(raw_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty audio payload received")

    if not groq_client:
        raise HTTPException(
            status_code=500, 
            detail="GROQ_API_KEY is not configured. Please set GROQ_API_KEY in environment or asr_server.py."
        )

    # Normalize language: handle Swagger 'string', full names, aliases, and ISO codes
    whisper_lang = None
    if language:
        clean_lang = language.strip().lower()
        if clean_lang in AUTO_DETECT_KEYWORDS:
            whisper_lang = None  # Automatic detection
        elif clean_lang in ["or", "odia"]:
            raise HTTPException(
                status_code=400,
                detail="Odia ('or') is not supported by OpenAI Whisper. Please use an Indic-specific ASR model for Odia."
            )
        elif clean_lang in LANGUAGE_NAME_MAP:
            whisper_lang = LANGUAGE_NAME_MAP[clean_lang]
        elif clean_lang in LANGUAGE_ALIASES:
            whisper_lang = LANGUAGE_ALIASES[clean_lang]
        elif clean_lang in VALID_WHISPER_LANGUAGES:
            whisper_lang = clean_lang
        else:
            logger.warning(
                f"Unrecognized language parameter '{language}'. Falling back to automatic language detection."
            )
            whisper_lang = None

    filename = file.filename if file.filename else "audio.webm"

    try:
        logger.info(f"🎙️ Transcribing audio (raw param: '{language}' -> resolved Whisper lang: '{whisper_lang}')")
        
        create_kwargs = {
            "file": (filename, raw_bytes, file.content_type or "audio/webm"),
            "model": "whisper-large-v3-turbo",
            "prompt": UNIVERSAL_BANKING_PROMPT,
            "response_format": "verbose_json"
        }
        if whisper_lang:
            create_kwargs["language"] = whisper_lang

        response = groq_client.audio.transcriptions.create(**create_kwargs)
        
        transcribed_text = response.text.strip()
        detected_lang = getattr(response, 'language', whisper_lang or 'auto')
        
        duration_seconds = getattr(response, 'duration', 0.0)
        audio_duration_ms = int(duration_seconds * 1000) if duration_seconds else 2000

        confidence = 0.92
        if hasattr(response, 'segments') and response.segments:
            first_seg = response.segments[0]
            if isinstance(first_seg, dict):
                avg_logprob = first_seg.get('avg_logprob', -0.2)
            else:
                avg_logprob = getattr(first_seg, 'avg_logprob', -0.2)
            confidence = round(min(max(float(2.71828 ** avg_logprob), 0.70), 0.99), 2)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API Call Failed for language '{language}': {e}")
        raise HTTPException(status_code=500, detail=f"ASR API Error: {str(e)}")

    return ASRResponseSchema(
        session_id=active_session_id,
        text=transcribed_text,
        confidence=confidence,
        language=detected_lang,
        audio_duration_ms=audio_duration_ms,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=ASR_HOST, port=ASR_PORT)
