"""
Configuration service for MemoryAid application
Manages environment variables and application settings
"""

import os
from functools import lru_cache
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # Security
    memory_api_key: str = Field(..., env="MEMORY_API_KEY")
    
    # Demo Mode
    demo_mode: bool = Field(False, env="DEMO_MODE")
    
    # Capture Configuration
    capture_interval_seconds: int = Field(900, env="CAPTURE_INTERVAL_SECONDS")  # 15 minutes default
    
    # Storage Paths
    storage_path: str = Field("./data/images", env="STORAGE_PATH")
    faiss_index_path: str = Field("./data/faiss.index", env="FAISS_INDEX_PATH")
    metadata_db_path: str = Field("./data/metadata.db", env="METADATA_DB_PATH")
    
    # S3 Configuration (Optional)
    s3_bucket_name: Optional[str] = Field(None, env="S3_BUCKET_NAME")
    s3_access_key: Optional[str] = Field(None, env="S3_ACCESS_KEY")
    s3_secret_key: Optional[str] = Field(None, env="S3_SECRET_KEY")
    s3_region: Optional[str] = Field(None, env="S3_REGION")
    
    # Development Settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    debug: bool = Field(False, env="DEBUG")
    
    # OpenAI Model Configuration
    openai_model: str = Field("gpt-4-vision-preview", env="OPENAI_MODEL")
    openai_embedding_model: str = Field("text-embedding-ada-002", env="OPENAI_EMBEDDING_MODEL")
    
    # Memory Search Configuration
    search_window_minutes: int = Field(30, env="SEARCH_WINDOW_MINUTES")
    max_search_results: int = Field(10, env="MAX_SEARCH_RESULTS")
    
    # Image Processing Configuration
    max_image_width: int = Field(1024, env="MAX_IMAGE_WIDTH")
    max_image_height: int = Field(1024, env="MAX_IMAGE_HEIGHT")
    image_quality: int = Field(70, env="IMAGE_QUALITY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()

def get_storage_path() -> str:
    """Get the storage path and ensure it exists"""
    settings = get_settings()
    os.makedirs(settings.storage_path, exist_ok=True)
    return settings.storage_path

def get_data_path() -> str:
    """Get the data directory path and ensure it exists"""
    data_path = "./data"
    os.makedirs(data_path, exist_ok=True)
    return data_path
