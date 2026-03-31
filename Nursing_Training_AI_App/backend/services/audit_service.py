"""
Audit Logging Service
Immutable audit trail for Enterprise compliance and security
"""

from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import uuid

class AuditAction(str, Enum):
    # User Actions
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_PASSWORD_CHANGED = "user.password_changed"
    USER_MFA_ENABLED = "user.mfa_enabled"
    USER_MFA_DISABLED = "user.mfa_disabled"
    USER_SSO_LOGIN = "user.sso_login"
    
    # Data Access
    DATA_VIEWED = "data.viewed"
    DATA_EXPORTED = "data.exported"
    DATA_DOWNLOADED = "data.downloaded"
    
    # Question Actions
    QUESTION_CREATED = "question.created"
    QUESTION_UPDATED = "question.updated"
    QUESTION_DELETED = "question.deleted"
    QUESTION_ANSWERED = "question.answered"
    
    # Subscription Actions
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    SUBSCRIPTION_RENEWED = "subscription.renewed"
    
    # Organization Actions
    ORG_CREATED = "org.created"
    ORG_UPDATED = "org.updated"
    ORG_DELETED = "org.deleted"
    ORG_SSO_CONFIGURED = "org.sso_configured"
    ORG_SETTINGS_CHANGED = "org.settings_changed"
    
    # Admin Actions
    ADMIN_USER_IMPERSONATION = "admin.user_impersonation"
    ADMIN_ROLE_ASSIGNED = "admin.role_assigned"
    ADMIN_ROLE_REVOKED = "admin.role_revoked"
    ADMIN_CONFIG_CHANGED = "admin.config_changed"
    ADMIN_CONTENT_MODERATED = "admin.content_moderated"
    
    # Security Events
    SECURITY_LOGIN_FAILED = "security.login_failed"
    SECURITY_MFA_FAILED = "security.mfa_failed"
    SECURITY_PASSWORD_RESET = "security.password_reset"
    SECURITY_SUSPICIOUS_ACTIVITY = "security.suspicious_activity"
    SECURITY_BREACH_ATTEMPT = "security.breach_attempt"
    
    # GDPR Events
    GDPR_DATA_EXPORT_REQUESTED = "gdpr.data_export_requested"
    GDPR_DATA_EXPORTED = "gdpr.data_exported"
    GDPR_DELETION_REQUESTED = "gdpr.deletion_requested"
    GDPR_DATA_DELETED = "gdpr.data_deleted"
    GDPR_CONSENT_GIVEN = "gdpr.consent_given"
    GDPR_CONSENT_WITHDRAWN = "gdpr.consent_withdrawn"

class AuditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SECURITY = "security"

class AuditService:
    """Service for creating immutable audit logs with DB persistence"""

    # Hardening constants
    MAX_DETAILS_SIZE = 5120  # 5 KB max per details dict
    MAX_STRING_FIELD = 500  # Max chars for string fields
    MAX_IN_MEMORY_LOGS = 1000  # Log rotation: keep last N in memory
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_MAX = 100  # max log entries per user per window

    def __init__(self):
        self.logs = []  # In-memory cache (fallback)
        self.previous_hash = "0" * 64  # Genesis hash
        self._db_available = False
        self._rate_tracker: Dict[str, list] = {}  # user_id -> [timestamps]

    def _get_db_session(self):
        try:
            from core.database import SessionLocal
            return SessionLocal()
        except Exception:
            return None

    async def initialize(self):
        """Incarca ultimul hash din DB la startup pentru continuitate chain"""
        db = self._get_db_session()
        if db:
            try:
                from models.security import AuditLog
                last = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
                if last:
                    self.previous_hash = last.hash
                    print(f"Audit chain restored from DB (last hash: {last.hash[:16]}...)")
                self._db_available = True
            except Exception as e:
                print(f"Warning: audit DB init failed: {e}")
            finally:
                db.close()

    def _sanitize_string(self, value: Optional[str], max_len: int = 0) -> Optional[str]:
        """Sanitizeaza string-uri: strip control chars, limiteaza lungimea"""
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        max_len = max_len or self.MAX_STRING_FIELD
        # Elimina control characters (except newline, tab)
        value = "".join(c for c in value if c >= ' ' or c in '\n\t')
        return value[:max_len]

    def _sanitize_details(self, details: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Sanitizeaza details dict: limiteaza dimensiunea, elimina date sensibile"""
        if not details:
            return {}
        # Serializeaza si verifica dimensiunea
        try:
            serialized = json.dumps(details, default=str)
        except (TypeError, ValueError):
            return {"_error": "non-serializable details"}
        if len(serialized) > self.MAX_DETAILS_SIZE:
            return {"_truncated": True, "_original_size": len(serialized),
                    "summary": serialized[:self.MAX_DETAILS_SIZE]}
        # Elimina campuri sensibile
        sensitive_keys = {"password", "token", "secret", "api_key", "authorization",
                         "cookie", "session_token", "hashed_password", "totp_secret"}
        cleaned = {}
        for k, v in details.items():
            if k.lower() in sensitive_keys:
                cleaned[k] = "[REDACTED]"
            elif isinstance(v, str) and len(v) > self.MAX_STRING_FIELD:
                cleaned[k] = v[:self.MAX_STRING_FIELD] + "...[truncated]"
            else:
                cleaned[k] = v
        return cleaned

    def _check_rate_limit(self, user_id: Optional[str]) -> bool:
        """Verifica rate limit per user. Returneaza True daca e OK, False daca e depasit."""
        key = user_id or "_anonymous"
        now = datetime.utcnow().timestamp()
        if key not in self._rate_tracker:
            self._rate_tracker[key] = []
        # Curata entries vechi
        cutoff = now - self.RATE_LIMIT_WINDOW
        self._rate_tracker[key] = [t for t in self._rate_tracker[key] if t > cutoff]
        if len(self._rate_tracker[key]) >= self.RATE_LIMIT_MAX:
            return False
        self._rate_tracker[key].append(now)
        return True

    def _rotate_in_memory_logs(self):
        """Pastreaza doar ultimele N loguri in memorie"""
        if len(self.logs) > self.MAX_IN_MEMORY_LOGS:
            self.logs = self.logs[-self.MAX_IN_MEMORY_LOGS:]

    async def log(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO
    ) -> Dict:
        """Create immutable audit log entry with DB persistence"""
        try:
            # Rate limiting
            if not self._check_rate_limit(user_id):
                return {"rate_limited": True, "action": action.value}

            # Sanitizare
            log_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "action": action.value,
                "severity": severity.value,
                "user_id": self._sanitize_string(user_id, 50),
                "organization_id": self._sanitize_string(organization_id, 50),
                "resource_type": self._sanitize_string(resource_type, 100),
                "resource_id": self._sanitize_string(resource_id, 100),
                "details": self._sanitize_details(details),
                "ip_address": self._sanitize_string(ip_address, 45),
                "user_agent": self._sanitize_string(user_agent, 300),
                "previous_hash": self.previous_hash
            }

            log_entry["hash"] = self._calculate_hash(log_entry)
            self.previous_hash = log_entry["hash"]

            # Persist in DB (primary storage)
            if self._db_available:
                db = self._get_db_session()
                if db:
                    try:
                        from models.security import AuditLog
                        record = AuditLog(
                            entry_id=log_entry["id"],
                            timestamp=datetime.fromisoformat(log_entry["timestamp"].rstrip("Z")),
                            action=log_entry["action"],
                            severity=log_entry["severity"],
                            user_id=log_entry["user_id"],
                            organization_id=log_entry["organization_id"],
                            resource_type=log_entry["resource_type"],
                            resource_id=log_entry["resource_id"],
                            ip_address=log_entry["ip_address"],
                            user_agent=log_entry["user_agent"],
                            details=log_entry["details"],
                            previous_hash=log_entry["previous_hash"],
                            hash=log_entry["hash"],
                        )
                        db.add(record)
                        db.commit()
                    except Exception as e:
                        db.rollback()
                        print(f"DB audit write failed, keeping in-memory: {e}")
                    finally:
                        db.close()

            # In-memory fallback cache + rotation
            self.logs.append(log_entry)
            self._rotate_in_memory_logs()

            if severity in [AuditSeverity.CRITICAL, AuditSeverity.SECURITY]:
                await self._alert_security_team(log_entry)

            return log_entry
        except Exception as e:
            print(f"Error creating audit log: {e}")
            raise
    
    def _calculate_hash(self, log_entry: Dict) -> str:
        """Calculate cryptographic hash of log entry for integrity"""
        try:
            # Create deterministic string from log entry
            hashable_data = json.dumps(
                {k: v for k, v in log_entry.items() if k != "hash"},
                sort_keys=True
            )
            
            # Calculate SHA-256 hash
            return hashlib.sha256(hashable_data.encode()).hexdigest()
        except Exception as e:
            print(f"Error calculating hash: {e}")
            raise
    
    def verify_log_integrity(self, log_entry: Dict) -> bool:
        """Verify that log entry hasn't been tampered with"""
        try:
            stored_hash = log_entry.get("hash")
            if not stored_hash:
                return False
            
            # Recalculate hash
            calculated_hash = self._calculate_hash(log_entry)
            
            return stored_hash == calculated_hash
        except Exception as e:
            print(f"Error verifying integrity: {e}")
            return False
    
    def verify_chain_integrity(self, logs: List[Dict]) -> Dict:
        """Verify entire audit log chain integrity"""
        try:
            results = {
                "valid": True,
                "total_logs": len(logs),
                "verified_logs": 0,
                "invalid_logs": [],
                "broken_chains": []
            }
            
            previous_hash = "0" * 64
            
            for i, log in enumerate(logs):
                # Verify individual log hash
                if not self.verify_log_integrity(log):
                    results["valid"] = False
                    results["invalid_logs"].append({"index": i, "id": log["id"]})
                
                # Verify chain linkage
                if log.get("previous_hash") != previous_hash:
                    results["valid"] = False
                    results["broken_chains"].append({"index": i, "id": log["id"]})
                
                previous_hash = log["hash"]
                results["verified_logs"] += 1
            
            return results
        except Exception as e:
            print(f"Error verifying chain: {e}")
            raise
    
    # ========================================
    # QUERY AUDIT LOGS
    # ========================================
    
    async def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        severity: Optional[AuditSeverity] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Query audit logs from DB with in-memory fallback"""
        if self._db_available:
            db = self._get_db_session()
            if db:
                try:
                    from models.security import AuditLog
                    query = db.query(AuditLog)

                    if user_id:
                        query = query.filter(AuditLog.user_id == user_id)
                    if organization_id:
                        query = query.filter(AuditLog.organization_id == organization_id)
                    if action:
                        query = query.filter(AuditLog.action == action.value)
                    if severity:
                        query = query.filter(AuditLog.severity == severity.value)
                    if date_from:
                        query = query.filter(AuditLog.timestamp >= date_from)
                    if date_to:
                        query = query.filter(AuditLog.timestamp <= date_to)

                    rows = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
                    return [
                        {
                            "id": r.entry_id, "timestamp": r.timestamp.isoformat() + "Z",
                            "action": r.action, "severity": r.severity,
                            "user_id": r.user_id, "organization_id": r.organization_id,
                            "resource_type": r.resource_type, "resource_id": r.resource_id,
                            "ip_address": r.ip_address, "user_agent": r.user_agent,
                            "details": r.details or {}, "previous_hash": r.previous_hash,
                            "hash": r.hash,
                        }
                        for r in rows
                    ]
                except Exception as e:
                    print(f"DB audit query failed, falling back to in-memory: {e}")
                finally:
                    db.close()

        # Fallback: in-memory
        filtered_logs = self.logs
        if user_id:
            filtered_logs = [l for l in filtered_logs if l.get("user_id") == user_id]
        if organization_id:
            filtered_logs = [l for l in filtered_logs if l.get("organization_id") == organization_id]
        if action:
            filtered_logs = [l for l in filtered_logs if l.get("action") == action.value]
        if severity:
            filtered_logs = [l for l in filtered_logs if l.get("severity") == severity.value]
        filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return filtered_logs[offset:offset + limit]
    
    async def get_user_activity_timeline(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict]:
        """Get user activity timeline"""
        try:
            date_from = datetime.now() - timedelta(days=days)
            
            logs = await self.get_audit_logs(
                user_id=user_id,
                date_from=date_from,
                limit=1000
            )
            
            # Group by day
            timeline = {}
            for log in logs:
                date = log["timestamp"][:10]
                if date not in timeline:
                    timeline[date] = []
                timeline[date].append(log)
            
            return [
                {"date": date, "activities": activities}
                for date, activities in sorted(timeline.items(), reverse=True)
            ]
        except Exception as e:
            print(f"Error getting activity timeline: {e}")
            raise
    
    # ========================================
    # SECURITY MONITORING
    # ========================================
    
    async def _alert_security_team(self, log_entry: Dict):
        """Alert security team for critical events"""
        try:
            # TODO: Send alert via email, Slack, PagerDuty
            print(f"🚨 SECURITY ALERT: {log_entry['action']}")
            print(f"User: {log_entry.get('user_id')}")
            print(f"Details: {log_entry.get('details')}")
            
            # TODO: Integrate with alerting service
        except Exception as e:
            print(f"Error alerting security team: {e}")
    
    async def detect_suspicious_activity(self, user_id: str) -> Dict:
        """Detect suspicious activity patterns"""
        try:
            # Get recent logs for user
            recent_logs = await self.get_audit_logs(
                user_id=user_id,
                date_from=datetime.now() - timedelta(hours=24)
            )
            
            suspicious = {
                "user_id": user_id,
                "is_suspicious": False,
                "reasons": [],
                "risk_score": 0
            }
            
            # Check for multiple failed logins
            failed_logins = [
                l for l in recent_logs 
                if l["action"] == AuditAction.SECURITY_LOGIN_FAILED.value
            ]
            if len(failed_logins) > 5:
                suspicious["is_suspicious"] = True
                suspicious["reasons"].append("Multiple failed login attempts")
                suspicious["risk_score"] += 30
            
            # Check for unusual IP addresses
            ip_addresses = set(l.get("ip_address") for l in recent_logs if l.get("ip_address"))
            if len(ip_addresses) > 5:
                suspicious["is_suspicious"] = True
                suspicious["reasons"].append("Multiple IP addresses")
                suspicious["risk_score"] += 20
            
            # Check for data export
            exports = [
                l for l in recent_logs 
                if l["action"] == AuditAction.DATA_EXPORTED.value
            ]
            if len(exports) > 10:
                suspicious["is_suspicious"] = True
                suspicious["reasons"].append("Excessive data exports")
                suspicious["risk_score"] += 40
            
            # If suspicious, log security event
            if suspicious["is_suspicious"]:
                await self.log(
                    action=AuditAction.SECURITY_SUSPICIOUS_ACTIVITY,
                    user_id=user_id,
                    details=suspicious,
                    severity=AuditSeverity.SECURITY
                )
            
            return suspicious
        except Exception as e:
            print(f"Error detecting suspicious activity: {e}")
            raise
    
    # ========================================
    # COMPLIANCE REPORTING
    # ========================================
    
    async def generate_compliance_report(
        self,
        organization_id: str,
        report_type: str,  # gdpr, soc2, iso27001
        date_from: datetime,
        date_to: datetime
    ) -> Dict:
        """Generate compliance report from audit logs"""
        try:
            logs = await self.get_audit_logs(
                organization_id=organization_id,
                date_from=date_from,
                date_to=date_to,
                limit=10000
            )
            
            report = {
                "report_type": report_type,
                "organization_id": organization_id,
                "period": {
                    "from": date_from.isoformat(),
                    "to": date_to.isoformat()
                },
                "generated_at": datetime.now().isoformat(),
                "total_events": len(logs),
                "events_by_type": {},
                "security_events": [],
                "data_access_events": [],
                "user_management_events": []
            }
            
            # Categorize events
            for log in logs:
                action = log["action"]
                report["events_by_type"][action] = report["events_by_type"].get(action, 0) + 1
                
                if log["severity"] == AuditSeverity.SECURITY.value:
                    report["security_events"].append(log)
                
                if "data." in action:
                    report["data_access_events"].append(log)
                
                if "user." in action:
                    report["user_management_events"].append(log)
            
            return report
        except Exception as e:
            print(f"Error generating compliance report: {e}")
            raise

# Singleton instance
audit_service = AuditService()

# Decorator for automatic audit logging
def audit_log(action: AuditAction, severity: AuditSeverity = AuditSeverity.INFO):
    """Decorator to automatically audit log function calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)
            
            # Create audit log
            # TODO: Extract user_id, org_id from context
            await audit_service.log(
                action=action,
                details={"function": func.__name__, "args": str(args)[:200]},
                severity=severity
            )
            
            return result
        return wrapper
    return decorator

