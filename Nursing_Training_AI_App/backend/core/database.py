"""
Enterprise Database Configuration
Connection pooling, read replicas, and optimizations
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import os
from contextlib import contextmanager

# Database URLs
PRIMARY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/nursing_ai")
READ_REPLICA_URLS = os.getenv("READ_REPLICA_URLS", "").split(",") if os.getenv("READ_REPLICA_URLS") else []

# Connection Pool Configuration (Enterprise-grade)
POOL_CONFIG = {
    "poolclass": QueuePool,
    "pool_size": 20,              # Number of permanent connections
    "max_overflow": 40,           # Additional connections if needed
    "pool_timeout": 30,           # Seconds to wait for connection
    "pool_recycle": 3600,         # Recycle connections after 1 hour
    "pool_pre_ping": True,        # Test connections before using
    "echo": False,                # Don't log SQL in production
    "echo_pool": False,           # Don't log pool events
}

# Create engines
primary_engine = create_engine(
    PRIMARY_DATABASE_URL,
    **POOL_CONFIG
)

# Create read replica engines
read_replica_engines = [
    create_engine(url, **POOL_CONFIG)
    for url in READ_REPLICA_URLS
    if url.strip()
]

# Session factory for primary (writes)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=primary_engine
)

# Session factory for read replicas (reads only)
if read_replica_engines:
    ReadSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=read_replica_engines[0]  # Simple round-robin can be added
    )
else:
    ReadSessionLocal = SessionLocal  # Fallback to primary

# Base class for models
Base = declarative_base()

# ========================================
# DATABASE SESSION MANAGEMENT
# ========================================

def get_db() -> Generator[Session, None, None]:
    """
    Get database session for write operations
    Use in FastAPI endpoints with Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_read_db() -> Generator[Session, None, None]:
    """
    Get database session for read-only operations
    Routes read queries to read replicas for better performance
    """
    db = ReadSessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# ========================================
# CONNECTION POOL MONITORING
# ========================================

def get_pool_status() -> dict:
    """Get connection pool status for monitoring"""
    try:
        pool = primary_engine.pool
        
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
            "pool_config": {
                "pool_size": POOL_CONFIG["pool_size"],
                "max_overflow": POOL_CONFIG["max_overflow"],
                "timeout": POOL_CONFIG["pool_timeout"]
            }
        }
    except Exception as e:
        print(f"Error getting pool status: {e}")
        return {}

# ========================================
# DATABASE OPTIMIZATION
# ========================================

@event.listens_for(primary_engine, "connect")
def set_connection_pragmas(dbapi_conn, connection_record):
    """Set connection-level optimizations"""
    cursor = dbapi_conn.cursor()
    
    # PostgreSQL optimizations
    cursor.execute("SET SESSION synchronous_commit = OFF")  # Faster writes
    cursor.execute("SET SESSION work_mem = '256MB'")        # More memory for sorts
    cursor.execute("SET SESSION maintenance_work_mem = '512MB'")
    
    cursor.close()

# ========================================
# READ REPLICA ROUTING
# ========================================

class ReadReplicaRouter:
    """Smart routing for read queries to replicas"""
    
    def __init__(self):
        self.current_replica = 0
        self.replica_count = len(read_replica_engines)
    
    def get_read_engine(self):
        """Get next read replica in round-robin fashion"""
        if not read_replica_engines:
            return primary_engine
        
        engine = read_replica_engines[self.current_replica]
        self.current_replica = (self.current_replica + 1) % self.replica_count
        return engine

read_replica_router = ReadReplicaRouter()

# ========================================
# DATABASE HEALTH CHECK
# ========================================

async def check_database_health() -> dict:
    """Check database health and connectivity"""
    try:
        with get_db_context() as db:
            # Test query
            result = db.execute("SELECT 1").scalar()
            
            # Check connection pool
            pool_status = get_pool_status()
            
            # Check query performance
            # TODO: Check slow query log
            
            health = {
                "status": "healthy" if result == 1 else "unhealthy",
                "primary_connected": result == 1,
                "read_replicas_count": len(read_replica_engines),
                "pool_status": pool_status,
                "avg_query_time_ms": None  # TODO: Calculate from metrics
            }
            
            return health
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# ========================================
# DATABASE INITIALIZATION
# ========================================

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=primary_engine)
    print("✅ Database tables created")

def drop_db():
    """Drop all database tables (WARNING: Use with caution!)"""
    Base.metadata.drop_all(bind=primary_engine)
    print("⚠️ Database tables dropped")
