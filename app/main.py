import logging
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.integrations.bank_api import bank_api
from app.routers import turn, speech

# Configure Logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("brain_service")

# Initialize FastAPI App
app = FastAPI(
    title="Tamil Nadu Vernacular Voice Micro-Banking Assistant - Brain Service",
    version="1.0.0",
    description="Tamil-first & Tanglish voice brain service for micro-loans, SHG savings, and crop loans."
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(turn.router)
app.include_router(speech.router)


@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 Voice Brain Service starting on Port {settings.PORT}...")
    logger.info(f"🎙️ ASR Mode: '{settings.ASR_MODE}' | ASR Base URL: '{settings.ASR_BASE_URL}'")
    logger.info(f"🏦 Bank API URL: '{settings.BANK_API_BASE_URL}'")


@app.get("/health", tags=["Health"])
async def health_check():
    """General health check endpoint"""
    return {
        "status": "ok",
        "service": "voice_brain_service",
        "port": settings.PORT,
        "environment": settings.ENVIRONMENT,
        "asr_mode": settings.ASR_MODE
    }


@app.get("/health/asr", tags=["Health"])
async def health_check_asr():
    """ASR microservice health check endpoint"""
    if settings.ASR_MODE == "local":
        return {
            "status": "ok",
            "asr_mode": "local",
            "message": "Local in-process ASR engine active"
        }

    url = f"{settings.ASR_BASE_URL.rstrip('/')}/health"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return {
                    "status": "ok",
                    "asr_mode": "http",
                    "asr_base_url": settings.ASR_BASE_URL,
                    "asr_response": resp.json()
                }
            return {
                "status": "warning",
                "asr_mode": "http",
                "asr_base_url": settings.ASR_BASE_URL,
                "http_code": resp.status_code
            }
    except Exception as e:
        return {
            "status": "error",
            "asr_mode": "http",
            "asr_base_url": settings.ASR_BASE_URL,
            "error_detail": str(e)
        }


@app.get("/v1/test-db", tags=["Health & Diagnostics"])
async def test_db_connection():
    """Test endpoint to verify live backend database connection to friend's machine"""
    try:
        profile = await bank_api.get_customer_360(settings.DEFAULT_DEMO_CUSTOMER_ID)
        balance = await bank_api.get_account_balance(settings.DEFAULT_DEMO_CUSTOMER_ID)
        return {
            "status": "connected",
            "backend_url": settings.BANK_API_BASE_URL,
            "demo_customer_profile": profile.model_dump(),
            "account_balance": balance
        }
    except Exception as e:
        return {
            "status": "error",
            "backend_url": settings.BANK_API_BASE_URL,
            "error_detail": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
