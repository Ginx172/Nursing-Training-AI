"""
🗄️ Database Configuration pentru Nursing Training AI
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
from core.config import settings

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_db():
    """Dependency pentru obținerea sesiunii de bază de date"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    """Dependency pentru obținerea conexiunii Redis"""
    return redis_client


async def init_db():
    """Inițializarea bazei de date (tolerantă când serviciile nu sunt pornite)"""
    # Test DB connection (non-fatal if not available)
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful")
    except Exception as e:
        print(f"⚠️  Database not available: {e}")
    
    # Test Redis (non-fatal if not available)
    try:
        redis_client.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"⚠️  Redis not available: {e}")
    
    # Optional: create tables if using SQLite/dev
    # Base.metadata.create_all(bind=engine)


async def close_db():
    """Închide conexiunile la baza de date"""
    try:
        engine.dispose()
        redis_client.close()
        print("✅ Database connections closed")
    except Exception as e:
        print(f"❌ Error closing database connections: {e}")
