"""
Payment API Endpoints
Handles subscription creation, management, and billing
"""

from fastapi import APIRouter, HTTPException, Request, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import stripe

from services.stripe_service import stripe_service
from config.stripe_config import (
    SubscriptionTier,
    STRIPE_WEBHOOK_SECRET,
    get_plan_details
)

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Request/Response Models
class CreateCustomerRequest(BaseModel):
    email: EmailStr
    name: str
    user_id: str
    nmc_number: Optional[str] = None
    current_band: str
    sector: str

class CreateSubscriptionRequest(BaseModel):
    customer_id: str
    tier: SubscriptionTier
    billing_cycle: str = "monthly"  # monthly or annual
    trial_days: int = 14

class CreateCheckoutSessionRequest(BaseModel):
    user_id: str
    tier: SubscriptionTier
    billing_cycle: str = "monthly"
    success_url: str
    cancel_url: str

class UpdateSubscriptionRequest(BaseModel):
    subscription_id: str
    new_tier: SubscriptionTier
    billing_cycle: str = "monthly"

class CancelSubscriptionRequest(BaseModel):
    subscription_id: str
    immediately: bool = False  # If False, cancel at period end

# Endpoints

@router.get("/plans")
async def get_subscription_plans():
    """Get all available subscription plans"""
    plans = []
    for tier in SubscriptionTier:
        plan_details = get_plan_details(tier)
        plans.append({
            "tier": tier.value,
            **plan_details
        })
    
    return {"success": True, "plans": plans}

@router.post("/customers/create")
async def create_customer(request: CreateCustomerRequest):
    """Create a new Stripe customer"""
    try:
        customer = await stripe_service.create_customer(
            email=request.email,
            name=request.name,
            metadata={
                "user_id": request.user_id,
                "nmc_number": request.nmc_number or "",
                "current_band": request.current_band,
                "sector": request.sector
            }
        )
        
        return {
            "success": True,
            "customer_id": customer.id,
            "email": customer.email
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/checkout/create-session")
async def create_checkout_session(request: CreateCheckoutSessionRequest):
    """Create a Stripe Checkout Session"""
    try:
        # Get plan details
        plan = get_plan_details(request.tier)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Get price ID based on billing cycle
        price_id = (
            plan.get("stripe_price_id_annual") 
            if request.billing_cycle == "annual" 
            else plan.get("stripe_price_id_monthly")
        )
        
        if not price_id:
            raise HTTPException(status_code=400, detail="Invalid billing cycle")
        
        # Get or create customer
        # TODO: Get customer_id from database based on user_id
        customer_id = "cus_example"  # Placeholder
        
        # Create checkout session
        session = await stripe_service.create_checkout_session(
            customer_id=customer_id,
            price_id=price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            trial_days=plan.get("features", {}).get("trial_days", 14)
        )
        
        return {
            "success": True,
            "session_id": session.id,
            "session_url": session.url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/subscriptions/create")
async def create_subscription(request: CreateSubscriptionRequest):
    """Create a subscription directly (without Checkout)"""
    try:
        plan = get_plan_details(request.tier)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        price_id = (
            plan.get("stripe_price_id_annual") 
            if request.billing_cycle == "annual" 
            else plan.get("stripe_price_id_monthly")
        )
        
        subscription = await stripe_service.create_subscription(
            customer_id=request.customer_id,
            price_id=price_id,
            trial_days=request.trial_days
        )
        
        return {
            "success": True,
            "subscription_id": subscription.id,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/subscriptions/{subscription_id}")
async def get_subscription(subscription_id: str):
    """Get subscription details"""
    try:
        subscription = await stripe_service.get_subscription(subscription_id)
        
        return {
            "success": True,
            "subscription": {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": subscription.canceled_at,
                "trial_end": subscription.trial_end
            }
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/subscriptions/update")
async def update_subscription(request: UpdateSubscriptionRequest):
    """Update subscription (upgrade/downgrade)"""
    try:
        plan = get_plan_details(request.new_tier)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        new_price_id = (
            plan.get("stripe_price_id_annual") 
            if request.billing_cycle == "annual" 
            else plan.get("stripe_price_id_monthly")
        )
        
        subscription = await stripe_service.update_subscription(
            subscription_id=request.subscription_id,
            new_price_id=new_price_id
        )
        
        return {
            "success": True,
            "subscription_id": subscription.id,
            "status": subscription.status,
            "message": "Subscription updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/subscriptions/cancel")
async def cancel_subscription(request: CancelSubscriptionRequest):
    """Cancel a subscription"""
    try:
        subscription = await stripe_service.cancel_subscription(
            subscription_id=request.subscription_id,
            at_period_end=not request.immediately
        )
        
        return {
            "success": True,
            "subscription_id": subscription.id,
            "status": subscription.status,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "message": "Subscription cancelled successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/subscriptions/reactivate")
async def reactivate_subscription(subscription_id: str):
    """Reactivate a cancelled subscription"""
    try:
        subscription = await stripe_service.reactivate_subscription(subscription_id)
        
        return {
            "success": True,
            "subscription_id": subscription.id,
            "status": subscription.status,
            "message": "Subscription reactivated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/billing-portal")
async def create_billing_portal_session(customer_id: str, return_url: str):
    """Create billing portal session for customer"""
    try:
        session = await stripe_service.create_billing_portal_session(
            customer_id=customer_id,
            return_url=return_url
        )
        
        return {
            "success": True,
            "portal_url": session.url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/invoice/upcoming")
async def get_upcoming_invoice(customer_id: str):
    """Get upcoming invoice for customer"""
    try:
        invoice = await stripe_service.get_upcoming_invoice(customer_id)
        
        if not invoice:
            return {"success": True, "invoice": None}
        
        return {
            "success": True,
            "invoice": {
                "amount_due": invoice.amount_due / 100,  # Convert pence to pounds
                "currency": invoice.currency,
                "period_start": invoice.period_start,
                "period_end": invoice.period_end,
                "next_payment_attempt": invoice.next_payment_attempt
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        
        # Verify webhook signature
        event = await stripe_service.construct_webhook_event(
            payload=payload,
            sig_header=stripe_signature,
            webhook_secret=STRIPE_WEBHOOK_SECRET
        )
        
        # Handle different event types
        event_type = event['type']
        event_data = event['data']['object']
        
        if event_type == 'customer.subscription.created':
            await handle_subscription_created(event_data)
        
        elif event_type == 'customer.subscription.updated':
            await handle_subscription_updated(event_data)
        
        elif event_type == 'customer.subscription.deleted':
            await handle_subscription_deleted(event_data)
        
        elif event_type == 'invoice.payment_succeeded':
            await handle_payment_succeeded(event_data)
        
        elif event_type == 'invoice.payment_failed':
            await handle_payment_failed(event_data)
        
        return {"success": True, "event_type": event_type}
        
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Webhook Event Handlers

async def handle_subscription_created(subscription: dict):
    """Handle new subscription creation"""
    print(f"Subscription created: {subscription['id']}")
    # TODO: Update database with new subscription
    # TODO: Grant access to features based on plan
    # TODO: Send welcome email

async def handle_subscription_updated(subscription: dict):
    """Handle subscription update"""
    print(f"Subscription updated: {subscription['id']}")
    # TODO: Update database
    # TODO: Adjust feature access if plan changed

async def handle_subscription_deleted(subscription: dict):
    """Handle subscription cancellation"""
    print(f"Subscription deleted: {subscription['id']}")
    # TODO: Revoke feature access
    # TODO: Send cancellation confirmation email

async def handle_payment_succeeded(invoice: dict):
    """Handle successful payment"""
    print(f"Payment succeeded: {invoice['id']}")
    # TODO: Record payment in database
    # TODO: Send payment receipt
    # TODO: Extend subscription period

async def handle_payment_failed(invoice: dict):
    """Handle failed payment"""
    print(f"Payment failed: {invoice['id']}")
    # TODO: Notify user of payment failure
    # TODO: Implement retry logic
    # TODO: Suspend access if payment not resolved

