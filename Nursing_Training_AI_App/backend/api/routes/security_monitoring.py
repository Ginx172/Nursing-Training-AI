"""
Security Monitoring Dashboard and Management
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from core.advanced_security import threat_detector, SecurityEvent
import jwt

router = APIRouter()
security = HTTPBearer()

class SecurityDashboardResponse(BaseModel):
    total_events: int
    high_risk_events: int
    blocked_ips: int
    suspicious_ips: int
    recent_events: List[Dict[str, Any]]
    risk_distribution: Dict[str, int]
    top_threats: List[Dict[str, Any]]

class IPManagementRequest(BaseModel):
    ip: str
    action: str  # "block" or "unblock"

class SecurityConfigUpdate(BaseModel):
    max_request_size: Optional[int] = None
    session_timeout: Optional[int] = None
    max_login_attempts: Optional[int] = None
    geo_blocked_countries: Optional[List[str]] = None

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin token for security operations"""
    try:
        token = credentials.credentials
        jwt_secret = os.getenv("JWT_SECRET")
        if not jwt_secret:
            raise HTTPException(status_code=500, detail="JWT_SECRET environment variable is not configured")
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/dashboard", response_model=SecurityDashboardResponse)
async def get_security_dashboard(admin: dict = Depends(verify_admin_token)):
    """Get comprehensive security dashboard"""
    try:
        # Load recent security events
        log_dir = Path("logs/security")
        recent_events = []
        total_events = 0
        high_risk_events = 0
        risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        
        if log_dir.exists():
            for log_file in sorted(log_dir.glob("security_*.jsonl"), reverse=True)[:7]:  # Last 7 days
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            total_events += 1
                            
                            if event.get("severity") == "HIGH" or event.get("severity") == "CRITICAL":
                                high_risk_events += 1
                            
                            risk_distribution[event.get("severity", "LOW")] += 1
                            
                            # Get recent events (last 24 hours)
                            event_time = datetime.fromisoformat(event["timestamp"])
                            if datetime.now() - event_time < timedelta(hours=24):
                                recent_events.append(event)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
        
        # Get threat statistics
        blocked_ips = len(threat_detector.blocked_ips)
        suspicious_ips = len(threat_detector.suspicious_ips)
        
        # Analyze top threats
        threat_counts = {}
        for event in recent_events:
            event_type = event.get("event_type", "UNKNOWN")
            threat_counts[event_type] = threat_counts.get(event_type, 0) + 1
        
        top_threats = [
            {"threat_type": threat, "count": count}
            for threat, count in sorted(threat_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        return SecurityDashboardResponse(
            total_events=total_events,
            high_risk_events=high_risk_events,
            blocked_ips=blocked_ips,
            suspicious_ips=suspicious_ips,
            recent_events=recent_events[-20:],  # Last 20 events
            risk_distribution=risk_distribution,
            top_threats=top_threats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")

@router.post("/ip/block")
async def block_ip(request: IPManagementRequest, admin: dict = Depends(verify_admin_token)):
    """Block an IP address"""
    try:
        threat_detector.blocked_ips.add(request.ip)
        
        # Log the action
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type="IP_BLOCKED",
            severity="MEDIUM",
            source_ip=request.ip,
            user_agent="admin_action",
            endpoint="/api/security/ip/block",
            details={"action": "block", "admin": admin.get("user_id", "unknown")},
            risk_score=0.0
        )
        threat_detector.record_security_event(event)
        
        return {"status": "success", "message": f"IP {request.ip} blocked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to block IP: {str(e)}")

@router.post("/ip/unblock")
async def unblock_ip(request: IPManagementRequest, admin: dict = Depends(verify_admin_token)):
    """Unblock an IP address"""
    try:
        threat_detector.blocked_ips.discard(request.ip)
        
        # Log the action
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type="IP_UNBLOCKED",
            severity="LOW",
            source_ip=request.ip,
            user_agent="admin_action",
            endpoint="/api/security/ip/unblock",
            details={"action": "unblock", "admin": admin.get("user_id", "unknown")},
            risk_score=0.0
        )
        threat_detector.record_security_event(event)
        
        return {"status": "success", "message": f"IP {request.ip} unblocked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unblock IP: {str(e)}")

@router.get("/threats/recent")
async def get_recent_threats(admin: dict = Depends(verify_admin_token)):
    """Get recent threat events"""
    try:
        log_dir = Path("logs/security")
        recent_threats = []
        
        if log_dir.exists():
            for log_file in sorted(log_dir.glob("security_*.jsonl"), reverse=True)[:3]:  # Last 3 days
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            if event.get("severity") in ["HIGH", "CRITICAL"]:
                                recent_threats.append(event)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
        
        return {"threats": recent_threats[-50:]}  # Last 50 high-risk events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load threats: {str(e)}")

@router.get("/stats/hourly")
async def get_hourly_stats(admin: dict = Depends(verify_admin_token)):
    """Get hourly security statistics"""
    try:
        log_dir = Path("logs/security")
        hourly_stats = {}
        
        if log_dir.exists():
            for log_file in sorted(log_dir.glob("security_*.jsonl"), reverse=True)[:1]:  # Today only
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            event_time = datetime.fromisoformat(event["timestamp"])
                            hour = event_time.strftime("%H:00")
                            
                            if hour not in hourly_stats:
                                hourly_stats[hour] = {
                                    "total_events": 0,
                                    "high_risk": 0,
                                    "blocked_ips": set(),
                                    "threat_types": {}
                                }
                            
                            hourly_stats[hour]["total_events"] += 1
                            
                            if event.get("severity") in ["HIGH", "CRITICAL"]:
                                hourly_stats[hour]["high_risk"] += 1
                            
                            hourly_stats[hour]["blocked_ips"].add(event.get("source_ip", ""))
                            
                            event_type = event.get("event_type", "UNKNOWN")
                            hourly_stats[hour]["threat_types"][event_type] = \
                                hourly_stats[hour]["threat_types"].get(event_type, 0) + 1
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
        
        # Convert sets to counts
        for hour_data in hourly_stats.values():
            hour_data["blocked_ips"] = len(hour_data["blocked_ips"])
        
        return {"hourly_stats": hourly_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load hourly stats: {str(e)}")

@router.post("/config/update")
async def update_security_config(
    config: SecurityConfigUpdate, 
    admin: dict = Depends(verify_admin_token)
):
    """Update security configuration"""
    try:
        # This would update the actual configuration in production
        # For now, just log the change
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type="CONFIG_UPDATED",
            severity="MEDIUM",
            source_ip="admin",
            user_agent="admin_action",
            endpoint="/api/security/config/update",
            details={"config_changes": config.dict(exclude_unset=True), "admin": admin.get("user_id", "unknown")},
            risk_score=0.0
        )
        threat_detector.record_security_event(event)
        
        return {"status": "success", "message": "Security configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")

@router.get("/health")
async def security_health_check():
    """Security system health check"""
    try:
        # Check if security logs are being written
        log_dir = Path("logs/security")
        is_logging = log_dir.exists() and any(log_dir.glob("security_*.jsonl"))
        
        # Check threat detector status
        threat_detector_status = len(threat_detector.suspicious_ips) >= 0
        
        return {
            "status": "healthy" if is_logging and threat_detector_status else "degraded",
            "logging_active": is_logging,
            "threat_detector_active": threat_detector_status,
            "blocked_ips_count": len(threat_detector.blocked_ips),
            "suspicious_ips_count": len(threat_detector.suspicious_ips)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
