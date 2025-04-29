"""
Configuration module for the application.
Handles loading environment variables and application settings.
"""
import os
from pathlib import Path
# Correcting import for Pydantic v2
from pydantic.v1 import BaseSettings # Use pydantic.v1 for backward compatibility
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings class."""
    # API configuration
    DDOWNLOAD_API_KEY: str = os.getenv("DDOWNLOAD_API_KEY", "")
    DDOWNLOAD_API_URL: str = "https://api-v2.ddownload.com/api"
    DDOWNLOAD_DOWNLOAD_URL: str = "https://ddownload.com"
    
    # Application settings
    APP_NAME: str = "مُرفِق الملفات"  # Arabic name meaning "File Uploader"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    MAX_CONTENT_LENGTH: int = 500 * 1024 * 1024  # 500MB max upload size
    
    # File settings
    ALLOWED_EXTENSIONS: set = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "zip", "rar", "doc", "docx", "xls", "xlsx"}
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    LOG_DIR: Path = BASE_DIR / "logs"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        # Allow extra fields if needed, though BaseSettings handles this
        # extra = "ignore"

# Create settings instance
settings = Settings()

# Ensure log directory exists
os.makedirs(settings.LOG_DIR, exist_ok=True)
