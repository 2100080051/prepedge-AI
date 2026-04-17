import os
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "PrepEdge AI"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./prepedge.db"
    SQLALCHEMY_ECHO: bool = False
    
    # Nvidia NIM / OpenAI-compatible settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "meta/llama-3.1-8b-instruct"
    OPENAI_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_IMAGE_MODEL: str = "nvidia/sana"
    
    # Image Generation (Pollinations.ai)
    POLLINATIONS_API_KEY: str = os.getenv("POLLINATIONS_API_KEY", "")
    POLLINATIONS_MODEL: str = "flux"  # flux, flux-pro, flux-realism
    
    # Chroma settings
    CHROMA_COLLECTION_NAME: str = "prepedge_questions"
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    
    # Redis Cache settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = 3600  # 1 hour default
    
    # Celery Queue settings
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # Auth settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-fallback-super-secret-32+chars-long-key-1234567890!!")
    ALGORITHM: str = "HS256"

    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters. Set in .env')
        return v

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Resend Email Service
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL: str = os.getenv("RESEND_FROM_EMAIL", "noreply@prepedge.io")
    
    # Razorpay settings
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    
    # CORS settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Property aliases for backward compatibility
    @property
    def redis_url(self) -> str:
        return self.REDIS_URL
    
    @property
    def celery_broker_url(self) -> str:
        return self.CELERY_BROKER_URL
    
    @property
    def celery_result_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
