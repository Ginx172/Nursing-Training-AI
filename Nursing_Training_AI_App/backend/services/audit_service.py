"""
Audit Logging Service
Immutable audit trail for Enterprise compliance and security
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
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
    """Service for creating immutable audit logs"""
    
    def __init__(self):
        self.logs = []  # In production, this would be a database
        self.previous_hash = "0" * 64  # Genesis hash
    
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
        """Create immutable audit log entry"""
        try:
            # Create log entry
            log_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "action": action.value,
                "severity": severity.value,
                "user_id": user_id,
                "organization_id": organization_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details or {},
                "ip_address": ip_address,
                "user_agent": user_agent,
                "previous_hash": self.previous_hash
            }
            
            # Calculate hash for integrity (blockchain-style)
            log_entry["hash"] = self._calculate_hash(log_entry)
            self.previous_hash = log_entry["hash"]
            
            # Store log (in production: append-only database or log service)
            # TODO: Save to PostgreSQL audit table
            # TODO: Also send to external log service (Splunk, Sumo Logic)
            self.logs.append(log_entry)
            
            # For critical events, also alert
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
        """Query audit logs with filters"""
        try:
            # TODO: Implement database query
            filtered_logs = self.logs
            
            # Apply filters
            if user_id:
                filtered_logs = [l for l in filtered_logs if l.get("user_id") == user_id]
            
            if organization_id:
                filtered_logs = [l for l in filtered_logs if l.get("organization_id") == organization_id]
            
            if action:
                filtered_logs = [l for l in filtered_logs if l.get("action") == action.value]
            
            if severity:
                filtered_logs = [l for l in filtered_logs if l.get("severity") == severity.value]
            
            # Sort by timestamp (newest first)
            filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Apply pagination
            return filtered_logs[offset:offset + limit]
        except Exception as e:
            print(f"Error querying audit logs: {e}")
            raise
    
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

