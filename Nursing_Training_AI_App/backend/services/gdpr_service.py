"""
GDPR Compliance Service
Handles GDPR rights: access, erasure, portability, rectification
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import zipfile
import io
from enum import Enum

from services.audit_service import audit_service, AuditAction, AuditSeverity

class GDPRRequest(str, Enum):
    ACCESS = "access"              # Right to access
    ERASURE = "erasure"            # Right to be forgotten
    PORTABILITY = "portability"    # Data portability
    RECTIFICATION = "rectification" # Right to rectification
    RESTRICTION = "restriction"     # Restriction of processing
    OBJECTION = "objection"        # Right to object

class GDPRService:
    """Service for GDPR compliance"""
    
    def __init__(self):
        self.retention_period_days = 2555  # 7 years for healthcare data
        self.deletion_grace_period_days = 30  # 30 days to cancel deletion
    
    # ========================================
    # RIGHT TO ACCESS (Article 15)
    # ========================================
    
    async def handle_data_access_request(self, user_id: str) -> Dict:
        """Handle GDPR data access request - provide all user data"""
        try:
            # Audit log
            await audit_service.log(
                action=AuditAction.GDPR_DATA_EXPORT_REQUESTED,
                user_id=user_id,
                severity=AuditSeverity.INFO
            )
            
            # Collect all user data from various tables
            user_data = await self._collect_all_user_data(user_id)
            
            # Create comprehensive export
            gdpr_export = {
                "request_type": "data_access",
                "user_id": user_id,
                "generated_at": datetime.now().isoformat(),
                "data_categories": {
                    "personal_information": user_data.get("profile", {}),
                    "authentication": {
                        "email": user_data.get("email"),
                        "login_history": user_data.get("login_history", []),
                        "mfa_enabled": user_data.get("mfa_enabled", False)
                    },
                    "training_data": {
                        "questions_answered": user_data.get("questions_answered", []),
                        "progress": user_data.get("progress", {}),
                        "certificates": user_data.get("certificates", [])
                    },
                    "subscription": user_data.get("subscription", {}),
                    "payments": user_data.get("payments", []),
                    "audit_logs": user_data.get("audit_logs", [])
                },
                "data_processing_purposes": [
                    "Provide training services",
                    "Track progress and performance",
                    "Process payments",
                    "Send notifications",
                    "Improve service quality"
                ],
                "data_recipients": [
                    "Nursing Training AI platform",
                    "Stripe (payment processor)",
                    "AWS (cloud hosting)",
                    "Email service provider"
                ],
                "data_retention": f"{self.retention_period_days} days",
                "rights": [
                    "Right to access (this export)",
                    "Right to erasure",
                    "Right to portability",
                    "Right to rectification",
                    "Right to object"
                ]
            }
            
            # Audit log completion
            await audit_service.log(
                action=AuditAction.GDPR_DATA_EXPORTED,
                user_id=user_id,
                details={"export_size_kb": len(json.dumps(gdpr_export)) / 1024},
                severity=AuditSeverity.INFO
            )
            
            return gdpr_export
        except Exception as e:
            print(f"Error handling data access request: {e}")
            raise
    
    # ========================================
    # RIGHT TO ERASURE (Article 17)
    # ========================================
    
    async def handle_erasure_request(
        self,
        user_id: str,
        reason: str,
        immediate: bool = False
    ) -> Dict:
        """Handle GDPR right to be forgotten"""
        try:
            # Audit log
            await audit_service.log(
                action=AuditAction.GDPR_DELETION_REQUESTED,
                user_id=user_id,
                details={"reason": reason, "immediate": immediate},
                severity=AuditSeverity.WARNING
            )
            
            # Check if user has active subscription
            # TODO: Check subscription status
            has_active_subscription = False  # Placeholder
            
            if has_active_subscription and not immediate:
                return {
                    "success": False,
                    "message": "Please cancel your subscription before requesting deletion",
                    "subscription_status": "active"
                }
            
            deletion_date = datetime.now()
            if not immediate:
                # Grace period for user to cancel
                deletion_date = datetime.now() + timedelta(days=self.deletion_grace_period_days)
            
            # Schedule deletion
            deletion_request = {
                "user_id": user_id,
                "requested_at": datetime.now().isoformat(),
                "scheduled_deletion_date": deletion_date.isoformat(),
                "status": "scheduled",
                "reason": reason,
                "grace_period_days": 0 if immediate else self.deletion_grace_period_days,
                "can_cancel": not immediate
            }
            
            # TODO: Save deletion request to database
            # TODO: Send confirmation email
            
            if immediate:
                # Execute deletion now
                deletion_result = await self._execute_deletion(user_id)
                deletion_request["status"] = "completed"
                deletion_request["completed_at"] = datetime.now().isoformat()
                deletion_request["result"] = deletion_result
            
            return {
                "success": True,
                "deletion_request": deletion_request
            }
        except Exception as e:
            print(f"Error handling erasure request: {e}")
            raise
    
    async def _execute_deletion(self, user_id: str) -> Dict:
        """Execute actual user data deletion"""
        try:
            deletion_result = {
                "user_id": user_id,
                "deleted_at": datetime.now().isoformat(),
                "deleted_items": {}
            }
            
            # Delete from various tables
            tables_to_delete = [
                "users",
                "user_profile",
                "user_progress",
                "user_answers",
                "user_sessions",
                "user_certificates",
                "user_preferences"
            ]
            
            for table in tables_to_delete:
                # TODO: Actual database deletion
                count = 0  # Placeholder
                deletion_result["deleted_items"][table] = count
            
            # Anonymize audit logs (keep for compliance, but remove PII)
            await self._anonymize_audit_logs(user_id)
            
            # Cancel Stripe subscription if exists
            # TODO: Cancel in Stripe
            
            # Audit log
            await audit_service.log(
                action=AuditAction.GDPR_DATA_DELETED,
                user_id=user_id,
                details=deletion_result,
                severity=AuditSeverity.WARNING
            )
            
            return deletion_result
        except Exception as e:
            print(f"Error executing deletion: {e}")
            raise
    
    async def cancel_deletion_request(self, user_id: str) -> bool:
        """Cancel pending deletion request"""
        try:
            # TODO: Check if within grace period
            # TODO: Update deletion request status to cancelled
            
            await audit_service.log(
                action=AuditAction.USER_UPDATED,
                user_id=user_id,
                details={"action": "deletion_cancelled"},
                severity=AuditSeverity.INFO
            )
            
            return True
        except Exception as e:
            print(f"Error cancelling deletion: {e}")
            raise
    
    # ========================================
    # RIGHT TO DATA PORTABILITY (Article 20)
    # ========================================
    
    async def export_portable_data(self, user_id: str, format: str = "json") -> bytes:
        """Export user data in portable format"""
        try:
            # Collect all user data
            user_data = await self._collect_all_user_data(user_id)
            
            if format == "json":
                # Export as JSON
                json_data = json.dumps(user_data, indent=2, ensure_ascii=False)
                return json_data.encode()
            
            elif format == "csv":
                # TODO: Convert to CSV format
                pass
            
            elif format == "zip":
                # Create ZIP with multiple files
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add profile
                    zipf.writestr('profile.json', json.dumps(user_data.get("profile", {}), indent=2))
                    
                    # Add training data
                    zipf.writestr('training_data.json', json.dumps(user_data.get("training_data", {}), indent=2))
                    
                    # Add certificates
                    zipf.writestr('certificates.json', json.dumps(user_data.get("certificates", []), indent=2))
                
                return zip_buffer.getvalue()
            
            # Audit log
            await audit_service.log(
                action=AuditAction.DATA_EXPORTED,
                user_id=user_id,
                details={"format": format},
                severity=AuditSeverity.INFO
            )
            
            return json.dumps(user_data).encode()
        except Exception as e:
            print(f"Error exporting portable data: {e}")
            raise
    
    # ========================================
    # DATA COLLECTION HELPER
    # ========================================
    
    async def _collect_all_user_data(self, user_id: str) -> Dict:
        """Collect all user data from all tables"""
        try:
            # TODO: Fetch from actual database tables
            
            user_data = {
                "user_id": user_id,
                "email": "user@example.com",
                "profile": {
                    "name": "John Doe",
                    "nmc_number": "12A3456E",
                    "current_band": "band_5",
                    "sector": "nhs",
                    "specialty": "amu"
                },
                "training_data": {
                    "questions_answered": 247,
                    "accuracy": 82.5,
                    "completed_banks": []
                },
                "subscription": {},
                "payments": [],
                "login_history": [],
                "certificates": [],
                "audit_logs": []
            }
            
            return user_data
        except Exception as e:
            print(f"Error collecting user data: {e}")
            raise
    
    async def _anonymize_audit_logs(self, user_id: str):
        """Anonymize audit logs (remove PII but keep for compliance)"""
        try:
            # TODO: Update audit logs to replace user_id with "DELETED_USER"
            # and remove any PII from details
            pass
        except Exception as e:
            print(f"Error anonymizing audit logs: {e}")
    
    # ========================================
    # CONSENT MANAGEMENT
    # ========================================
    
    async def record_consent(
        self,
        user_id: str,
        consent_type: str,
        consented: bool,
        consent_text: str
    ) -> Dict:
        """Record user consent"""
        try:
            consent_record = {
                "user_id": user_id,
                "consent_type": consent_type,
                "consented": consented,
                "consent_text": consent_text,
                "timestamp": datetime.now().isoformat(),
                "ip_address": None,  # TODO: Get from request
                "user_agent": None   # TODO: Get from request
            }
            
            # TODO: Save to database
            
            # Audit log
            await audit_service.log(
                action=AuditAction.GDPR_CONSENT_GIVEN if consented else AuditAction.GDPR_CONSENT_WITHDRAWN,
                user_id=user_id,
                details=consent_record,
                severity=AuditSeverity.INFO
            )
            
            return consent_record
        except Exception as e:
            print(f"Error recording consent: {e}")
            raise
    
    async def get_user_consents(self, user_id: str) -> List[Dict]:
        """Get all consent records for user"""
        try:
            # TODO: Fetch from database
            return []
        except Exception as e:
            print(f"Error getting consents: {e}")
            raise

# Singleton instance
gdpr_service = GDPRService()

