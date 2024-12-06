import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Bank Check Parser"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    API_URL: str = "http://localhost:5000"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./checks.db")
    
    # OCR Settings
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "tesseract")
    SUPPORTED_LANGUAGES: List[str] = ["eng", "fra", "spa"]
    
    # Image Processing
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]
    
    # AI Model Settings
    MODEL_PATH: str = "models/fraud_detection_model.h5"
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Validation Settings
    MAX_CHECK_AGE_DAYS: int = 180
    MAX_AMOUNT: float = 10000000.0
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # Allow extra fields

settings = Settings() 