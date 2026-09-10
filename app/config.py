import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    PORT: int = 8001

    BANK_API_BASE_URL: str = "http://127.0.0.1:8000"
    BANK_API_TIMEOUT_SECONDS: float = 5.0

    FRIEND_GPU_OLLAMA_URL: str = "http://192.168.1.45:11434/v1"
    FRIEND_GPU_MODEL: str = "qwen2.5:7b"

    GROQ_API_KEY: str = "gsk_your_groq_api_key_here"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    LOCAL_OLLAMA_URL: str = "http://127.0.0.1:11434/v1"
    LOCAL_OLLAMA_MODEL: str = "qwen2.5:3b"

    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    SESSION_TTL_SECONDS: int = 1800

    DEFAULT_DEMO_CUSTOMER_ID: str = "00000000-0000-0000-0001-000000000001"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
