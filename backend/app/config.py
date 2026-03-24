import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "PrepEdge AI"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./prepedge.db"
    SQLALCHEMY_ECHO: bool = False
    
    # Nvidia NIM / OpenAI-compatible settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "meta/llama-3.1-8b-instruct"
    OPENAI_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_IMAGE_MODEL: str = "nvidia/sana"
    
    # Chroma settings
    CHROMA_COLLECTION_NAME: str = "prepedge_questions"
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    
    # Auth settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Razorpay settings
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    
    # CORS settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
