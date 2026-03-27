"""
Stripe Payment Service for Nursing Training AI
Handles subscriptions, payments, and billing
"""

import stripe
import asyncio
import os
from typing import Dict, Optional, List
from datetime import datetime
from functools import partial
from config.stripe_config import (
    STRIPE_SECRET_KEY,
    SUBSCRIPTION_PLANS,
    SubscriptionTier
)

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

class StripeService:
    """Service for handling all Stripe operations"""

    @staticmethod
    async def create_customer(
        email: str,
        name: str,
        metadata: Optional[Dict] = None
    ) -> stripe.Customer:
        """Create a new Stripe customer"""
        try:
            customer = await asyncio.to_thread(
                stripe.Customer.create,
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer
        except stripe.StripeError as e:
            print(f"Error creating customer: {e}")
            raise

    @staticmethod
    async def create_subscription(
        customer_id: str,
        price_id: str,
        trial_days: int = 14
    ) -> stripe.Subscription:
        """Create a new subscription for a customer"""
        try:
            subscription = await asyncio.to_thread(
                stripe.Subscription.create,
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days,
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )
            return subscription
        except stripe.StripeError as e:
            print(f"Error creating subscription: {e}")
            raise

    @staticmethod
    async def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        trial_days: int = 14
    ) -> stripe.checkout.Session:
        """Create a Checkout Session for subscription"""
        try:
            session = await asyncio.to_thread(
                stripe.checkout.Session.create,
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                subscription_data={
                    'trial_period_days': trial_days,
                },
                allow_promotion_codes=True,
                billing_address_collection='required'
            )
            return session
        except stripe.StripeError as e:
            print(f"Error creating checkout session: {e}")
            raise

    @staticmethod
    async def get_subscription(subscription_id: str) -> stripe.Subscription:
        """Get subscription details"""
        try:
            subscription = await asyncio.to_thread(
                stripe.Subscription.retrieve, subscription_id
            )
            return subscription
        except stripe.StripeError as e:
            print(f"Error retrieving subscription: {e}")
            raise

    @staticmethod
    async def update_subscription(
        subscription_id: str,
        new_price_id: str
    ) -> stripe.Subscription:
        """Update subscription (upgrade/downgrade)"""
        try:
            subscription = await asyncio.to_thread(
                stripe.Subscription.retrieve, subscription_id
            )
            subscription = await asyncio.to_thread(
                stripe.Subscription.modify,
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': new_price_id,
                }],
                proration_behavior='create_prorations'
            )
            return subscription
        except stripe.StripeError as e:
            print(f"Error updating subscription: {e}")
            raise

    @staticmethod
    async def cancel_subscription(
        subscription_id: str,
        at_period_end: bool = True
    ) -> stripe.Subscription:
        """Cancel a subscription"""
        try:
            if at_period_end:
                subscription = await asyncio.to_thread(
                    stripe.Subscription.modify,
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = await asyncio.to_thread(
                    stripe.Subscription.delete, subscription_id
                )
            return subscription
        except stripe.StripeError as e:
            print(f"Error cancelling subscription: {e}")
            raise

    @staticmethod
    async def reactivate_subscription(subscription_id: str) -> stripe.Subscription:
        """Reactivate a cancelled subscription"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False
            )
            return subscription
        except stripe.StripeError as e:
            print(f"Error reactivating subscription: {e}")
            raise

    @staticmethod
    async def create_payment_intent(
        amount: int,  # in pence (e.g., 999 = £9.99)
        customer_id: str,
        currency: str = 'gbp',
        metadata: Optional[Dict] = None
    ) -> stripe.PaymentIntent:
        """Create a payment intent for one-time payments"""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            return payment_intent
        except stripe.StripeError as e:
            print(f"Error creating payment intent: {e}")
            raise

    @staticmethod
    async def get_customer_subscriptions(customer_id: str) -> List[stripe.Subscription]:
        """Get all subscriptions for a customer"""
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status='all'
            )
            return subscriptions.data
        except stripe.StripeError as e:
            print(f"Error getting customer subscriptions: {e}")
            raise

    @staticmethod
    async def get_upcoming_invoice(customer_id: str) -> Optional[stripe.Invoice]:
        """Get upcoming invoice for a customer"""
        try:
            invoice = stripe.Invoice.upcoming(customer=customer_id)
            return invoice
        except stripe.InvalidRequestError:
            # No upcoming invoice
            return None
        except stripe.StripeError as e:
            print(f"Error getting upcoming invoice: {e}")
            raise

    @staticmethod
    async def create_billing_portal_session(
        customer_id: str,
        return_url: str
    ) -> stripe.billing_portal.Session:
        """Create a billing portal session for customer to manage subscription"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return session
        except stripe.StripeError as e:
            print(f"Error creating billing portal session: {e}")
            raise

    @staticmethod
    async def construct_webhook_event(
        payload: bytes,
        sig_header: str,
        webhook_secret: str
    ) -> stripe.Event:
        """Construct and verify webhook event"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError as e:
            print(f"Invalid payload: {e}")
            raise
        except stripe.SignatureVerificationError as e:
            print(f"Invalid signature: {e}")
            raise

    @staticmethod
    def get_plan_details(tier: SubscriptionTier) -> Dict:
        """Get subscription plan details"""
        return SUBSCRIPTION_PLANS.get(tier, {})

    @staticmethod
    def calculate_proration(
        current_tier: SubscriptionTier,
        new_tier: SubscriptionTier,
        billing_cycle: str = "monthly"
    ) -> Dict:
        """Calculate proration amount for plan change"""
        current_plan = SUBSCRIPTION_PLANS.get(current_tier, {})
        new_plan = SUBSCRIPTION_PLANS.get(new_tier, {})
        
        price_key = f"price_{billing_cycle}_gbp"
        current_price = current_plan.get(price_key, 0)
        new_price = new_plan.get(price_key, 0)
        
        difference = new_price - current_price
        
        return {
            "current_price": current_price,
            "new_price": new_price,
            "difference": difference,
            "is_upgrade": difference > 0,
            "proration_amount": abs(difference)
        }

    @staticmethod
    async def apply_coupon(
        subscription_id: str,
        coupon_code: str
    ) -> stripe.Subscription:
        """Apply a coupon code to subscription"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                coupon=coupon_code
            )
            return subscription
        except stripe.StripeError as e:
            print(f"Error applying coupon: {e}")
            raise

    @staticmethod
    async def create_usage_record(
        subscription_item_id: str,
        quantity: int,
        timestamp: Optional[int] = None
    ) -> stripe.UsageRecord:
        """Create usage record for metered billing (if needed)"""
        try:
            usage_record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=timestamp or int(datetime.now().timestamp())
            )
            return usage_record
        except stripe.StripeError as e:
            print(f"Error creating usage record: {e}")
            raise

# Singleton instance
stripe_service = StripeService()

