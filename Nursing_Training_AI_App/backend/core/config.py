"""
🔧 Configuration Settings pentru Nursing Training AI Backend
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Configurații principale ale aplicației"""
    
    # Aplicație
    APP_NAME: str = "Nursing Training AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"
    ALLOWED_HOSTS: str = "*"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string to list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS if isinstance(self.ALLOWED_ORIGINS, list) else ["*"]
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Parse ALLOWED_HOSTS string to list"""
        if isinstance(self.ALLOWED_HOSTS, str):
            if self.ALLOWED_HOSTS == "*":
                return ["*"]
            return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
        return self.ALLOWED_HOSTS if isinstance(self.ALLOWED_HOSTS, list) else ["*"]
    
    # Baza de date
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/nursing_training_ai"
    DATABASE_URL_TEST: str = "postgresql://user:password@localhost:5432/nursing_training_ai_test"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # RAG System
    RAG_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    
    # MCP System
    MCP_MODEL_PATH: Optional[str] = None
    MCP_CONTEXT_SIZE: int = 4096
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Email (pentru viitor)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Payment (pentru viitor)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Knowledge Base
    KNOWLEDGE_BASE_PATH: str = "./data/knowledge_base"
    
    # MCP and RAG Endpoints
    MCP_ENDPOINT: str = "http://localhost:8001/mcp"
    RAG_ENDPOINT: str = "http://localhost:8002/rag"
    
    # Logging
    AUDIT_LOG_PATH: str = "./logs/audit.log"
    TELEMETRY_LOG_PATH: str = "./logs/telemetry.log"
    
    # Geolocation
    GEOIP_DB_PATH: str = "./data/GeoLite2-Country.mmdb"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Instanță globală de configurație
settings = Settings()
