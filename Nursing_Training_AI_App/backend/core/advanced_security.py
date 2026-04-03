"""
Advanced Security Module - Maximum Security Hardening
"""

import re
import hashlib
import hmac
import secrets
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import ipaddress
import geoip2.database
import geoip2.errors
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

# Security Configuration
SECURITY_CONFIG = {
    "max_request_size": 10 * 1024 * 1024,  # 10MB
    "max_file_upload_size": 50 * 1024 * 1024,  # 50MB
    "session_timeout": 3600,  # 1 hour
    "max_login_attempts": 5,
    "lockout_duration": 900,  # 15 minutes
    "suspicious_patterns": [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"eval\s*\(",
        r"expression\s*\(",
        r"union\s+select",
        r"drop\s+table",
        r"delete\s+from",
        r"insert\s+into",
        r"update\s+set",
        r"exec\s*\(",
        r"xp_cmdshell",
        r"\.\./",
        r"\.\.\\",
        r"null\s+byte",
        r"\\x00",
        r"\\x0a",
        r"\\x0d"
    ],
    "allowed_file_extensions": [".pdf", ".doc", ".docx", ".txt", ".jpg", ".png", ".gif"],
    "max_filename_length": 255,
    "geo_blocked_countries": ["CN", "RU", "KP", "IR"],  # Block suspicious countries
    "allowed_ips": [],  # Empty means allow all, populate for whitelist
    "blocked_ips": [],  # IPs to block
    "rate_limits": {
        "login": {"requests": 5, "window": 300},  # 5 per 5 minutes
        "api": {"requests": 100, "window": 60},   # 100 per minute
        "upload": {"requests": 10, "window": 3600}  # 10 per hour
    }
}

@dataclass
class SecurityEvent:
    """Security event for monitoring"""
    timestamp: datetime
    event_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    source_ip: str
    user_agent: str
    endpoint: str
    details: Dict[str, Any]
    risk_score: float

class ThreatDetector:
    """Advanced threat detection system"""
    
    def __init__(self):
        self.suspicious_ips = {}
        self.failed_attempts = {}
        self.anomaly_scores = {}
        self.blocked_ips = set()
        self.geo_db_path = os.getenv("GEOIP_DB_PATH", "GeoLite2-Country.mmdb")
        
    def detect_sql_injection(self, input_text: str) -> bool:
        """Detect SQL injection attempts"""
        sql_patterns = [
            r"union\s+select", r"drop\s+table", r"delete\s+from",
            r"insert\s+into", r"update\s+set", r"exec\s*\(",
            r"xp_cmdshell", r"sp_executesql", r"'\s*or\s*'", r"'\s*and\s*'",
            r"1\s*=\s*1", r"'\s*=\s*'", r"or\s+1\s*=\s*1"
        ]
        return any(re.search(pattern, input_text, re.IGNORECASE) for pattern in sql_patterns)
    
    def detect_xss(self, input_text: str) -> bool:
        """Detect XSS attempts"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>", r"javascript:", r"vbscript:",
            r"onload\s*=", r"onerror\s*=", r"eval\s*\(",
            r"expression\s*\(", r"<iframe", r"<object",
            r"<embed", r"<link", r"<meta"
        ]
        return any(re.search(pattern, input_text, re.IGNORECASE) for pattern in xss_patterns)
    
    def detect_path_traversal(self, input_text: str) -> bool:
        """Detect path traversal attempts"""
        path_patterns = [r"\.\./", r"\.\.\\", r"\.\.%2f", r"\.\.%5c"]
        return any(re.search(pattern, input_text, re.IGNORECASE) for pattern in path_patterns)
    
    def detect_command_injection(self, input_text: str) -> bool:
        """Detect command injection attempts"""
        cmd_patterns = [
            r";\s*rm\s+", r";\s*del\s+", r";\s*cat\s+", r";\s*ls\s+",
            r"\|\s*rm\s+", r"\|\s*del\s+", r"\|\s*cat\s+", r"\|\s*ls\s+",
            r"`[^`]+`",  # Backtick execution (must have content)
            r"\$\([^)]+\)",  # $(cmd) execution (must have content)
            r"&&\s*(rm|del|cat|ls|wget|curl|sh|bash|chmod|kill)\s",  # && followed by dangerous command
            r"\|\|\s*(rm|del|cat|ls|wget|curl|sh|bash|chmod|kill)\s",  # || followed by dangerous command
        ]
        if not input_text or len(input_text) < 3:
            return False
        return any(re.search(pattern, input_text, re.IGNORECASE) for pattern in cmd_patterns)
    
    def calculate_risk_score(self, request: Request, input_data: str = "") -> float:
        """Calculate comprehensive risk score"""
        score = 0.0
        source_ip = request.client.host if request.client else "unknown"
        
        # IP reputation
        if source_ip in self.suspicious_ips:
            score += 30.0
        
        # Failed attempts
        if source_ip in self.failed_attempts:
            score += min(self.failed_attempts[source_ip] * 10, 50.0)
        
        # Geolocation
        try:
            country = self._get_country_from_ip(source_ip)
            if country in SECURITY_CONFIG["geo_blocked_countries"]:
                score += 40.0
        except (geoip2.errors.GeoIP2Error, FileNotFoundError, ValueError):
            pass
        
        # Input analysis
        if input_data:
            if self.detect_sql_injection(input_data):
                score += 50.0
            if self.detect_xss(input_data):
                score += 40.0
            if self.detect_path_traversal(input_data):
                score += 30.0
            if self.detect_command_injection(input_data):
                score += 60.0
        
        # User agent analysis
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            score += 20.0
        if any(bot in user_agent.lower() for bot in ["bot", "crawler", "spider", "scraper"]):
            score += 15.0
        
        # Request frequency
        current_time = time.time()
        if source_ip in self.anomaly_scores:
            recent_requests = [t for t in self.anomaly_scores[source_ip] if current_time - t < 60]
            if len(recent_requests) > 20:  # More than 20 requests per minute
                score += 25.0
        else:
            self.anomaly_scores[source_ip] = []
        self.anomaly_scores[source_ip].append(current_time)
        
        return min(score, 100.0)
    
    def _get_country_from_ip(self, ip: str) -> Optional[str]:
        """Get country from IP using GeoIP database"""
        try:
            with geoip2.database.Reader(self.geo_db_path) as reader:
                response = reader.country(ip)
                return response.country.iso_code
        except (geoip2.errors.GeoIP2Error, FileNotFoundError, ValueError):
            return None
    
    def record_security_event(self, event: SecurityEvent):
        """Record security event - in-memory + JSONL + DB"""
        # Store in memory for real-time analysis
        if event.source_ip not in self.suspicious_ips:
            self.suspicious_ips[event.source_ip] = []
        self.suspicious_ips[event.source_ip].append(event)

        # Log to JSONL file (backup/archive)
        self._log_security_event(event)

        # Persist to DB
        self._persist_event_to_db(event)

    def _persist_event_to_db(self, event: SecurityEvent):
        """Persist security event to PostgreSQL"""
        try:
            from core.database import SessionLocal
            from models.security import SecurityEvent as SecurityEventModel
            db = SessionLocal()
            try:
                ts = event.timestamp
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts)

                record = SecurityEventModel(
                    timestamp=ts,
                    event_type=event.event_type,
                    severity=event.severity,
                    source_ip=event.source_ip,
                    user_agent=event.user_agent,
                    endpoint=event.endpoint,
                    details=event.details,
                    risk_score=event.risk_score,
                )
                db.add(record)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"DB security event write failed: {e}")
            finally:
                db.close()
        except Exception:
            pass

    def _log_security_event(self, event: SecurityEvent):
        """Log security event to JSONL file (backup)"""
        if isinstance(event.timestamp, str):
            timestamp_str = event.timestamp
        else:
            timestamp_str = event.timestamp.isoformat()

        log_entry = {
            "timestamp": timestamp_str,
            "event_type": event.event_type,
            "severity": event.severity,
            "source_ip": event.source_ip,
            "user_agent": event.user_agent,
            "endpoint": event.endpoint,
            "details": event.details,
            "risk_score": event.risk_score
        }

        try:
            log_file = f"logs/security/security_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass

class InputSanitizer:
    """Advanced input sanitization"""
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not input_str:
            return ""
        
        # Remove null bytes
        input_str = input_str.replace("\x00", "")
        
        # Truncate if too long
        if len(input_str) > max_length:
            input_str = input_str[:max_length]
        
        # Remove control characters except newlines and tabs
        input_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', input_str)
        
        # Normalize unicode
        input_str = input_str.encode('utf-8', errors='ignore').decode('utf-8')
        
        return input_str.strip()
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate filename for security"""
        if not filename or len(filename) > SECURITY_CONFIG["max_filename_length"]:
            return False
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        if any(char in filename for char in dangerous_chars):
            return False
        
        # Check extension
        ext = os.path.splitext(filename)[1].lower()
        if ext not in SECURITY_CONFIG["allowed_file_extensions"]:
            return False
        
        return True
    
    @staticmethod
    def sanitize_json(input_data: Any) -> Any:
        """Sanitize JSON input recursively"""
        if isinstance(input_data, str):
            # Remove XSS and SQL injection patterns
            sanitized = InputSanitizer.sanitize_string(input_data)
            # Additional XSS removal
            sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE)
            sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
            # SQL injection removal
            sanitized = re.sub(r"';.*?--", '', sanitized, flags=re.IGNORECASE)
            return sanitized
        elif isinstance(input_data, dict):
            return {k: InputSanitizer.sanitize_json(v) for k, v in input_data.items()}
        elif isinstance(input_data, list):
            return [InputSanitizer.sanitize_json(item) for item in input_data]
        else:
            return input_data

class EncryptionManager:
    """Advanced encryption for sensitive data"""
    
    def __init__(self, master_key: Optional[str] = None):
        if master_key:
            self.key = self._derive_key(master_key)
        else:
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        salt = b'nursing_training_salt'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Encrypt dictionary values"""
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, str) and value:
                encrypted[key] = self.encrypt(value)
            else:
                encrypted[key] = str(value)
        return encrypted

class AdvancedSecurityMiddleware:
    """Advanced security middleware with comprehensive protection"""
    
    def __init__(self):
        self.threat_detector = ThreatDetector()
        self.input_sanitizer = InputSanitizer()
        self.encryption_manager = EncryptionManager()
        self.rate_limiter = {}
        self.blocked_ips = set(SECURITY_CONFIG["blocked_ips"])
        self.allowed_ips = set(SECURITY_CONFIG["allowed_ips"])
    
    async def __call__(self, request: Request, call_next):
        """Main security middleware"""
        source_ip = request.client.host if request.client else "unknown"
        
        # IP filtering
        if self._is_ip_blocked(source_ip):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Rate limiting
        if self._is_rate_limited(request):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Request size validation
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > SECURITY_CONFIG["max_request_size"]:
            raise HTTPException(status_code=413, detail="Request too large")
        
        # Threat detection
        risk_score = self.threat_detector.calculate_risk_score(request)
        if risk_score > 80:
            self._record_high_risk_event(request, risk_score)
            raise HTTPException(status_code=403, detail="Suspicious activity detected")
        
        # Input sanitization
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            if body:
                try:
                    # Try to parse as JSON and sanitize
                    json_data = json.loads(body.decode())
                    sanitized_data = self.input_sanitizer.sanitize_json(json_data)
                    # Re-encode the sanitized data
                    request._body = json.dumps(sanitized_data).encode()
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Daca nu e JSON, sanitizam ca string
                    sanitized_body = self.input_sanitizer.sanitize_string(body.decode(errors="ignore"))
                    request._body = sanitized_body.encode()
        
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';"
        
        return response
    
    def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        if ip in self.blocked_ips:
            return True
        if self.allowed_ips and ip not in self.allowed_ips:
            return True
        return False
    
    def _is_rate_limited(self, request: Request) -> bool:
        """Check rate limiting"""
        source_ip = request.client.host if request.client else "unknown"
        endpoint = request.url.path
        current_time = time.time()
        
        # Determine rate limit based on endpoint
        if "/login" in endpoint:
            limit_config = SECURITY_CONFIG["rate_limits"]["login"]
        elif "/upload" in endpoint:
            limit_config = SECURITY_CONFIG["rate_limits"]["upload"]
        else:
            limit_config = SECURITY_CONFIG["rate_limits"]["api"]
        
        key = f"{source_ip}:{endpoint}"
        if key not in self.rate_limiter:
            self.rate_limiter[key] = []
        
        # Clean old requests
        self.rate_limiter[key] = [
            t for t in self.rate_limiter[key] 
            if current_time - t < limit_config["window"]
        ]
        
        # Check if limit exceeded
        if len(self.rate_limiter[key]) >= limit_config["requests"]:
            return True
        
        # Add current request
        self.rate_limiter[key].append(current_time)
        return False
    
    def _record_high_risk_event(self, request: Request, risk_score: float):
        """Record high-risk security event"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type="HIGH_RISK_REQUEST",
            severity="HIGH",
            source_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", ""),
            endpoint=request.url.path,
            details={"risk_score": risk_score, "method": request.method},
            risk_score=risk_score
        )
        self.threat_detector.record_security_event(event)

# Global instances
threat_detector = ThreatDetector()
input_sanitizer = InputSanitizer()
encryption_manager = EncryptionManager()
advanced_security_middleware = AdvancedSecurityMiddleware()
