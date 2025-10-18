"""
Webhook Service
Enterprise webhook system for event notifications to third-party systems
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
import hmac
import hashlib
import json
from enum import Enum
import asyncio

class WebhookEvent(str, Enum):
    # User Events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGGED_IN = "user.logged_in"
    
    # Training Events
    QUESTION_ANSWERED = "question.answered"
    BANK_COMPLETED = "bank.completed"
    CERTIFICATE_EARNED = "certificate.earned"
    ACHIEVEMENT_UNLOCKED = "achievement.unlocked"
    
    # Subscription Events
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
    
    # Organization Events
    ORG_USER_ADDED = "org.user_added"
    ORG_USER_REMOVED = "org.user_removed"
    ORG_SETTINGS_CHANGED = "org.settings_changed"
    
    # Compliance Events
    GDPR_EXPORT_COMPLETED = "gdpr.export_completed"
    GDPR_DELETION_COMPLETED = "gdpr.deletion_completed"

class WebhookService:
    """Service for managing and delivering webhooks"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delays = [60, 300, 900]  # 1min, 5min, 15min
        self.timeout_seconds = 30
    
    # ========================================
    # WEBHOOK REGISTRATION
    # ========================================
    
    async def register_webhook(
        self,
        organization_id: str,
        url: str,
        events: List[WebhookEvent],
        secret: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """Register a webhook endpoint"""
        try:
            if not secret:
                # Generate webhook secret
                secret = self._generate_webhook_secret()
            
            webhook = {
                "id": self._generate_webhook_id(),
                "organization_id": organization_id,
                "url": url,
                "events": [e.value for e in events],
                "secret": secret,
                "description": description,
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "last_triggered": None,
                "delivery_stats": {
                    "total_deliveries": 0,
                    "successful_deliveries": 0,
                    "failed_deliveries": 0
                }
            }
            
            # TODO: Save to database
            
            return webhook
        except Exception as e:
            print(f"Error registering webhook: {e}")
            raise
    
    async def update_webhook(
        self,
        webhook_id: str,
        updates: Dict[str, Any]
    ) -> Dict:
        """Update webhook configuration"""
        try:
            # TODO: Update in database
            return {"success": True, "webhook_id": webhook_id}
        except Exception as e:
            print(f"Error updating webhook: {e}")
            raise
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook"""
        try:
            # TODO: Delete from database
            return True
        except Exception as e:
            print(f"Error deleting webhook: {e}")
            raise
    
    # ========================================
    # WEBHOOK DELIVERY
    # ========================================
    
    async def trigger_webhook(
        self,
        organization_id: str,
        event: WebhookEvent,
        payload: Dict[str, Any]
    ) -> Dict:
        """Trigger webhook for specific event"""
        try:
            # Get all webhooks for this organization and event
            webhooks = await self._get_webhooks_for_event(organization_id, event)
            
            if not webhooks:
                return {"delivered": 0, "failed": 0}
            
            # Prepare event payload
            event_payload = {
                "event": event.value,
                "timestamp": datetime.now().isoformat(),
                "organization_id": organization_id,
                "data": payload
            }
            
            # Deliver to all registered webhooks
            results = []
            for webhook in webhooks:
                result = await self._deliver_webhook(webhook, event_payload)
                results.append(result)
            
            # Summary
            delivered = sum(1 for r in results if r["success"])
            failed = len(results) - delivered
            
            return {
                "delivered": delivered,
                "failed": failed,
                "results": results
            }
        except Exception as e:
            print(f"Error triggering webhook: {e}")
            raise
    
    async def _deliver_webhook(
        self,
        webhook: Dict,
        payload: Dict[str, Any],
        retry_count: int = 0
    ) -> Dict:
        """Deliver webhook with retry logic"""
        try:
            # Generate signature
            signature = self._generate_signature(payload, webhook["secret"])
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature,
                "X-Webhook-Event": payload["event"],
                "X-Webhook-Delivery-ID": self._generate_delivery_id(),
                "User-Agent": "NursingTrainingAI-Webhooks/1.0"
            }
            
            # Send webhook
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    webhook["url"],
                    json=payload,
                    headers=headers
                )
            
            success = response.status_code in [200, 201, 202, 204]
            
            # Log delivery
            delivery_log = {
                "webhook_id": webhook["id"],
                "event": payload["event"],
                "url": webhook["url"],
                "status_code": response.status_code,
                "success": success,
                "retry_count": retry_count,
                "timestamp": datetime.now().isoformat(),
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
            
            # TODO: Save delivery log to database
            
            if not success and retry_count < self.max_retries:
                # Retry after delay
                delay = self.retry_delays[retry_count]
                await asyncio.sleep(delay)
                return await self._deliver_webhook(webhook, payload, retry_count + 1)
            
            return delivery_log
        
        except Exception as e:
            print(f"Webhook delivery error: {e}")
            
            # Retry logic
            if retry_count < self.max_retries:
                delay = self.retry_delays[retry_count]
                await asyncio.sleep(delay)
                return await self._deliver_webhook(webhook, payload, retry_count + 1)
            
            return {
                "webhook_id": webhook["id"],
                "success": False,
                "error": str(e),
                "retry_count": retry_count
            }
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _generate_signature(self, payload: Dict, secret: str) -> str:
        """Generate HMAC signature for webhook verification"""
        message = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def verify_webhook_signature(
        self,
        payload: Dict,
        signature: str,
        secret: str
    ) -> bool:
        """Verify webhook signature"""
        expected_signature = self._generate_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    def _generate_webhook_secret(self) -> str:
        """Generate secure webhook secret"""
        import secrets
        return f"whsec_{secrets.token_urlsafe(32)}"
    
    def _generate_webhook_id(self) -> str:
        """Generate webhook ID"""
        import uuid
        return f"wh_{uuid.uuid4().hex[:16]}"
    
    def _generate_delivery_id(self) -> str:
        """Generate delivery ID for tracking"""
        import uuid
        return f"whd_{uuid.uuid4().hex[:16]}"
    
    async def _get_webhooks_for_event(
        self,
        organization_id: str,
        event: WebhookEvent
    ) -> List[Dict]:
        """Get webhooks subscribed to specific event"""
        try:
            # TODO: Fetch from database
            # Filter by organization_id and event
            return []
        except Exception as e:
            print(f"Error getting webhooks: {e}")
            return []
    
    # ========================================
    # WEBHOOK MANAGEMENT
    # ========================================
    
    async def get_webhook_deliveries(
        self,
        webhook_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """Get delivery history for webhook"""
        try:
            # TODO: Fetch from database
            return []
        except Exception as e:
            print(f"Error getting deliveries: {e}")
            return []
    
    async def retry_failed_delivery(self, delivery_id: str) -> Dict:
        """Manually retry failed webhook delivery"""
        try:
            # TODO: Get delivery from database
            # TODO: Re-send webhook
            return {"success": True}
        except Exception as e:
            print(f"Error retrying delivery: {e}")
            raise
    
    async def test_webhook(self, webhook_id: str) -> Dict:
        """Send test event to webhook"""
        try:
            # TODO: Get webhook from database
            
            test_payload = {
                "event": "webhook.test",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "message": "This is a test webhook delivery"
                }
            }
            
            # TODO: Deliver webhook
            
            return {
                "success": True,
                "message": "Test webhook sent"
            }
        except Exception as e:
            print(f"Error testing webhook: {e}")
            raise

# Singleton instance
webhook_service = WebhookService()

