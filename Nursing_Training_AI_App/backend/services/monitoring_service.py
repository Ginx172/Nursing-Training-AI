"""
Monitoring Service
Application Performance Monitoring (APM) and System Health
"""

from typing import Dict, List
from datetime import datetime
import time
import psutil
import asyncio

class MonitoringService:
    """Service for monitoring application health and performance"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
    
    def track_request(self, endpoint: str, method: str, duration_ms: float, status_code: int):
        """Track API request metrics"""
        self.request_count += 1
        self.response_times.append(duration_ms)
        
        if status_code >= 400:
            self.error_count += 1
        
        # TODO: Log to monitoring service (Sentry, DataDog, etc.)
        
        if duration_ms > 2000:  # Alert if response > 2s
            print(f"⚠️ Slow request: {method} {endpoint} took {duration_ms}ms")
    
    def get_system_health(self) -> Dict:
        """Get current system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            avg_response_time = (
                sum(self.response_times) / len(self.response_times) 
                if self.response_times else 0
            )
            
            error_rate = (
                (self.error_count / self.request_count * 100) 
                if self.request_count > 0 else 0
            )
            
            health = {
                "status": "healthy" if cpu_percent < 80 and memory.percent < 85 else "warning",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": uptime,
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                },
                "application": {
                    "requests_total": self.request_count,
                    "errors_total": self.error_count,
                    "error_rate_percent": round(error_rate, 2),
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "requests_per_second": self.request_count / uptime if uptime > 0 else 0
                }
            }
            
            return health
        except Exception as e:
            print(f"Error getting system health: {e}")
            return {"status": "error", "error": str(e)}
    
    def check_database_health(self) -> Dict:
        """Check database connectivity and performance"""
        try:
            from core.database import primary_engine, get_pool_status
            from sqlalchemy import text

            with primary_engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()

            pool = get_pool_status()

            return {
                "status": "healthy" if result == 1 else "unhealthy",
                "primary_connected": result == 1,
                "pool_status": pool,
            }
        except Exception as e:
            return {"status": "unhealthy", "primary_connected": False, "error": str(e)}
    
    def check_redis_health(self) -> Dict:
        """Check Redis cache health"""
        try:
            import redis
            r = redis.Redis.from_url("redis://localhost:6379/0", socket_timeout=2)
            r.ping()
            info = r.info("memory")
            return {
                "status": "healthy",
                "memory_used_mb": round(info.get("used_memory", 0) / (1024 * 1024), 1),
            }
        except Exception:
            return {"status": "unavailable", "note": "Redis not running (optional for core features)"}
    
    def get_comprehensive_health_check(self) -> Dict:
        """Get comprehensive system health check"""
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {
                "api": self.get_system_health(),
                "database": self.check_database_health(),
                "cache": self.check_redis_health()
            }
        }

# Singleton instance
monitoring_service = MonitoringService()

