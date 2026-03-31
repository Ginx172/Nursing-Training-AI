"""
Configuration Settings for Nursing Training AI Backend
Secure configuration with mandatory validation for production
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import os
import sys
import secrets


class Settings(BaseSettings):
    """Application configuration - sensitive fields have NO defaults"""

    # Application
    APP_NAME: str = "Nursing Training AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS - safe defaults for local development only
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, str):
            origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
            return origins if origins else []
        return self.ALLOWED_ORIGINS if isinstance(self.ALLOWED_ORIGINS, list) else []

    @property
    def allowed_hosts_list(self) -> List[str]:
        if isinstance(self.ALLOWED_HOSTS, str):
            return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]
        return self.ALLOWED_HOSTS if isinstance(self.ALLOWED_HOSTS, list) else []

    # Database - NO default with password
    DATABASE_URL: str
    DATABASE_URL_TEST: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT - NO insecure default
    SECRET_KEY: str
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
    MAX_FILE_SIZE: int = 10485760

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Payment
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # RAG Hub (unified search)
    RAG_CHROMADB_PATH: str = "./data/vectordb"
    RAG_REINDEX_ON_STARTUP: bool = False
    RAG_QUESTIONS_COLLECTION: str = "nursing_questions"

    # Ollama (local AI orchestrator)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"
    OLLAMA_ENABLED: bool = True
    OLLAMA_TIMEOUT: int = 300

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

    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        placeholder_values = [
            "your-secret-key-change-in-production",
            "your-secret-key-here",
            "changeme",
            "secret",
        ]
        if v.lower() in placeholder_values:
            raise ValueError("SECRET_KEY is set to an insecure placeholder.")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters.")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        placeholder_passwords = ["password", "nursing_password", "pass", "changeme"]
        for placeholder in placeholder_passwords:
            if ":" + placeholder + "@" in v:
                raise ValueError("DATABASE_URL contains placeholder password: " + placeholder)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


def _load_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        print("\n" + "=" * 60)
        print("CONFIGURATION ERROR - Cannot start application")
        print("=" * 60)
        print("\n" + str(e) + "\n")
        print("Required environment variables:")
        print("  DATABASE_URL=postgresql://user:password@host:5432/dbname")
        print("  SECRET_KEY=<at-least-32-character-random-string>")
        print("=" * 60 + "\n")
        sys.exit(1)


settings = _load_settings()
