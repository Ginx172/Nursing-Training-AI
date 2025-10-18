"""
Teste pentru verificarea plăților și webhook-uri Stripe
"""

import pytest
import hmac
import hashlib
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open
import os

# Import the main app
from main import app

client = TestClient(app)

class TestPaymentVerification:
    """Teste pentru endpoint-ul de verificare plăți generic"""
    
    def test_payment_verification_valid_signature(self):
        """Test verificare plăți cu semnătură validă"""
        payload = {
            "provider": "test_provider",
            "payload": {"amount": "100.00", "currency": "USD"},
            "signature": "valid_signature_123456789"
        }
        
        response = client.post("/api/security/payments/verify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "verified"
        assert data["provider"] == "test_provider"
    
    def test_payment_verification_invalid_signature(self):
        """Test verificare plăți cu semnătură invalidă"""
        payload = {
            "provider": "test_provider",
            "payload": {"amount": "100.00", "currency": "USD"},
            "signature": "short"
        }
        
        response = client.post("/api/security/payments/verify", json=payload)
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]
    
    def test_payment_verification_missing_signature(self):
        """Test verificare plăți fără semnătură"""
        payload = {
            "provider": "test_provider",
            "payload": {"amount": "100.00", "currency": "USD"},
            "signature": ""
        }
        
        response = client.post("/api/security/payments/verify", json=payload)
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]


class TestStripeWebhook:
    """Teste pentru webhook-ul Stripe cu verificare HMAC"""
    
    def setup_method(self):
        """Setup pentru fiecare test"""
        self.stripe_secret = "whsec_test_secret_key_12345"
        self.test_payload = b'{"id": "evt_test_webhook", "type": "payment_intent.succeeded"}'
        
    def _generate_stripe_signature(self, payload: bytes, secret: str) -> str:
        """Generează semnătura Stripe pentru testare"""
        timestamp = "1234567890"
        signed_payload = f"{timestamp}.{payload.decode()}"
        signature = hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"t={timestamp},v1={signature}"
    
    @patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test_secret_key_12345"})
    def test_stripe_webhook_valid_signature(self):
        """Test webhook Stripe cu semnătură validă"""
        signature = self._generate_stripe_signature(self.test_payload, self.stripe_secret)
        
        response = client.post(
            "/api/security/payments/stripe/webhook",
            content=self.test_payload,
            headers={"Stripe-Signature": signature}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    @patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test_secret_key_12345"})
    def test_stripe_webhook_invalid_signature(self):
        """Test webhook Stripe cu semnătură invalidă"""
        invalid_signature = "t=1234567890,v1=invalid_signature"
        
        response = client.post(
            "/api/security/payments/stripe/webhook",
            content=self.test_payload,
            headers={"Stripe-Signature": invalid_signature}
        )
        
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]
    
    @patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test_secret_key_12345"})
    def test_stripe_webhook_missing_signature(self):
        """Test webhook Stripe fără header de semnătură"""
        response = client.post(
            "/api/security/payments/stripe/webhook",
            content=self.test_payload
        )
        
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]
    
    def test_stripe_webhook_no_secret_configured(self):
        """Test webhook Stripe când secretul nu este configurat"""
        with patch.dict(os.environ, {}, clear=True):
            response = client.post(
                "/api/security/payments/stripe/webhook",
                content=self.test_payload,
                headers={"Stripe-Signature": "t=1234567890,v1=test"}
            )
            
            assert response.status_code == 500
            assert "Stripe secret not configured" in response.json()["detail"]
    
    @patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test_secret_key_12345"})
    def test_stripe_webhook_empty_payload(self):
        """Test webhook Stripe cu payload gol"""
        signature = self._generate_stripe_signature(b"", self.stripe_secret)
        
        response = client.post(
            "/api/security/payments/stripe/webhook",
            content=b"",
            headers={"Stripe-Signature": signature}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestAuditLogging:
    """Teste pentru audit logging în endpoint-urile de plăți"""
    
    @patch('core.audit.audit.log')
    def test_payment_verification_audit_logging(self, mock_audit_log):
        """Test că verificarea plăților generează log-uri de audit"""
        payload = {
            "provider": "test_provider",
            "payload": {"amount": "100.00"},
            "signature": "valid_signature_123456789"
        }
        
        response = client.post("/api/security/payments/verify", json=payload)
        assert response.status_code == 200
        
        # Verifică că audit.log a fost apelat
        mock_audit_log.assert_called_once()
        call_args = mock_audit_log.call_args
        assert call_args[1]["actor"] == "test_provider"
        assert call_args[1]["action"] == "payment.verify"
        assert call_args[1]["resource"] == "webhook"
        assert call_args[1]["details"]["ok"] is True
    
    @patch('core.audit.audit.log')
    @patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test_secret_key_12345"})
    def test_stripe_webhook_audit_logging(self, mock_audit_log):
        """Test că webhook-ul Stripe generează log-uri de audit"""
        test_payload = b'{"id": "evt_test", "type": "payment_intent.succeeded"}'
        secret = "whsec_test_secret_key_12345"
        signature = hmac.new(
            secret.encode(),
            f"1234567890.{test_payload.decode()}".encode(),
            hashlib.sha256
        ).hexdigest()
        stripe_signature = f"t=1234567890,v1={signature}"
        
        response = client.post(
            "/api/security/payments/stripe/webhook",
            content=test_payload,
            headers={"Stripe-Signature": stripe_signature}
        )
        
        assert response.status_code == 200
        
        # Verifică că audit.log a fost apelat
        mock_audit_log.assert_called_once()
        call_args = mock_audit_log.call_args
        assert call_args[1]["actor"] == "stripe"
        assert call_args[1]["action"] == "webhook.accept"
        assert call_args[1]["resource"] == "payments"
        assert "bytes" in call_args[1]["details"]


class TestSecurityMiddleware:
    """Teste pentru middleware-urile de securitate"""
    
    def test_security_headers(self):
        """Test că header-urile de securitate sunt setate"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "0"
        assert response.headers["Referrer-Policy"] == "no-referrer"
        assert "Permissions-Policy" in response.headers
    
    def test_rate_limiting(self):
        """Test că rate limiting funcționează"""
        # Fă mai multe request-uri rapid pentru a testa rate limiting
        responses = []
        for i in range(130):  # Peste limita de 120/minut
            response = client.get("/")
            responses.append(response)
        
        # Cel puțin unul ar trebui să fie rate limited
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
