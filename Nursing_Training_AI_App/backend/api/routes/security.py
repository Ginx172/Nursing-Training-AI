from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Dict
import hmac
import hashlib
import os
from core.audit import audit


router = APIRouter()


class PaymentVerificationRequest(BaseModel):
    provider: str
    payload: Dict[str, str]
    signature: str


@router.post("/payments/verify")
async def verify_payment(req: PaymentVerificationRequest):
    # Stub de verificare a semnăturii; înlocuiește cu verificare reală (ex: Stripe/Webhook secret)
    if not req.signature or len(req.signature) < 16:
        raise HTTPException(status_code=400, detail="Invalid signature")
    # TODO: verificare criptografică HMAC cu secretul providerului
    audit.log(actor=req.provider, action="payment.verify", resource="webhook", details={"ok": True})
    return {"status": "verified", "provider": req.provider}


@router.post("/payments/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Stripe secret not configured")
    payload = await request.body()
    # Parse Stripe-Signature header (format: t=timestamp,v1=signature)
    if not stripe_signature:
        audit.log(actor="stripe", action="webhook.reject", resource="payments", details={"reason": "missing signature"})
        raise HTTPException(status_code=400, detail="Invalid signature")

    sig_parts = dict(pair.split("=", 1) for pair in stripe_signature.split(",") if "=" in pair)
    timestamp = sig_parts.get("t", "")
    received_sig = sig_parts.get("v1", "")

    if not timestamp or not received_sig:
        audit.log(actor="stripe", action="webhook.reject", resource="payments", details={"reason": "malformed signature header"})
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Compute expected signature using Stripe's signed-payload scheme
    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, received_sig):
        audit.log(actor="stripe", action="webhook.reject", resource="payments", details={"reason": "bad signature"})
        raise HTTPException(status_code=400, detail="Invalid signature")
    audit.log(actor="stripe", action="webhook.accept", resource="payments", details={"bytes": len(payload)})
    return {"status": "ok"}


