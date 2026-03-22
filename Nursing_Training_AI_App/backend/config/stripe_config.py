"""
Stripe Configuration for Nursing Training AI
Defines subscription plans and payment settings
"""

import os
from typing import Dict, List
from enum import Enum

class SubscriptionTier(str, Enum):
    DEMO = "demo"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

# Stripe API Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

def get_plan_details(tier: SubscriptionTier) -> Dict:
    """Get details for a specific subscription tier"""
    return SUBSCRIPTION_PLANS.get(tier, {})

# Subscription Plans Configuration
SUBSCRIPTION_PLANS = {
    SubscriptionTier.DEMO: {
        "name": "Demo Plan",
        "description": "Try before you buy - Limited access",
        "price_monthly_gbp": 0.00,
        "price_annual_gbp": 0.00,
        "stripe_price_id_monthly": "",  # No Stripe product for free tier
        "stripe_price_id_annual": "",
        "features": {
            "question_banks_access": 10,  # Only 10 banks
            "questions_per_day": 20,
            "specialties_access": ["amu"],  # Only AMU
            "sectors_access": ["nhs"],  # Only NHS
            "bands_access": ["band_2", "band_3", "band_4", "band_5"],  # Up to Band 5
            "audio_features": False,
            "offline_mode": False,
            "progress_tracking": True,
            "basic_analytics": True,
            "ai_feedback": False,
            "personalized_recommendations": False,
            "certificates": False,
            "priority_support": False,
            "trial_days": 14,
            "max_users": 1
        },
        "limitations": [
            "Limited to 20 questions per day",
            "Only AMU specialty available",
            "Only NHS sector",
            "Bands 2-5 only",
            "No audio features",
            "No offline mode",
            "Basic analytics only",
            "14-day trial only"
        ]
    },
    
    SubscriptionTier.BASIC: {
        "name": "Basic Plan",
        "description": "Perfect for individual healthcare professionals",
        "price_monthly_gbp": 9.99,
        "price_annual_gbp": 99.00,  # 2 months free
        "stripe_price_id_monthly": "price_basic_monthly",  # TODO: Replace with actual Stripe Price ID
        "stripe_price_id_annual": "price_basic_annual",
        "features": {
            "question_banks_access": 500,  # 500 banks
            "questions_per_day": 100,
            "specialties_access": ["amu", "emergency", "icu", "maternity", "mental_health"],
            "sectors_access": ["nhs", "care_homes"],
            "bands_access": ["band_2", "band_3", "band_4", "band_5", "band_6"],
            "audio_features": True,
            "offline_mode": True,
            "offline_banks_limit": 5,
            "progress_tracking": True,
            "basic_analytics": True,
            "ai_feedback": True,
            "personalized_recommendations": True,
            "certificates": False,
            "priority_support": False,
            "max_users": 1
        },
        "benefits": [
            "500 question banks access",
            "100 questions per day",
            "5 NHS specialties",
            "NHS + Care Homes sectors",
            "Bands 2-6",
            "Audio features (TTS + STT)",
            "Offline mode (5 banks)",
            "AI-powered feedback",
            "Personalized recommendations",
            "Progress tracking"
        ]
    },
    
    SubscriptionTier.PROFESSIONAL: {
        "name": "Professional Plan",
        "description": "For serious healthcare professionals advancing their career",
        "price_monthly_gbp": 19.99,
        "price_annual_gbp": 199.00,  # ~2 months free
        "stripe_price_id_monthly": "price_professional_monthly",
        "stripe_price_id_annual": "price_professional_annual",
        "features": {
            "question_banks_access": -1,  # Unlimited
            "questions_per_day": -1,  # Unlimited
            "specialties_access": "all",  # All 9 specialties
            "sectors_access": "all",  # All 5 sectors
            "bands_access": "all",  # All bands 2-8d
            "audio_features": True,
            "offline_mode": True,
            "offline_banks_limit": 20,
            "progress_tracking": True,
            "advanced_analytics": True,
            "ai_feedback": True,
            "personalized_recommendations": True,
            "certificates": True,
            "cpd_tracking": True,
            "study_groups": True,
            "priority_support": True,
            "email_support": True,
            "max_users": 1
        },
        "benefits": [
            "✅ UNLIMITED question banks",
            "✅ UNLIMITED questions per day",
            "✅ ALL 9 specialties (NHS)",
            "✅ ALL 5 sectors (NHS, Private, Care Homes, Community, Primary Care)",
            "✅ ALL bands (2 through 8d)",
            "✅ Audio features (TTS + STT)",
            "✅ Offline mode (20 banks)",
            "✅ Advanced analytics dashboard",
            "✅ AI-powered feedback",
            "✅ Personalized learning paths",
            "✅ CPD certificates",
            "✅ CPD hours tracking",
            "✅ Study groups",
            "✅ Priority email support"
        ],
        "popular": True  # Mark as most popular
    },
    
    SubscriptionTier.ENTERPRISE: {
        "name": "Enterprise Plan",
        "description": "For healthcare organizations and training departments",
        "price_monthly_gbp": 199.00,
        "price_annual_gbp": 1999.00,  # ~2 months free
        "stripe_price_id_monthly": "price_enterprise_monthly",
        "stripe_price_id_annual": "price_enterprise_annual",
        "features": {
            "question_banks_access": -1,  # Unlimited
            "questions_per_day": -1,  # Unlimited
            "specialties_access": "all",
            "sectors_access": "all",
            "bands_access": "all",
            "audio_features": True,
            "offline_mode": True,
            "offline_banks_limit": -1,  # Unlimited
            "progress_tracking": True,
            "advanced_analytics": True,
            "team_analytics": True,
            "ai_feedback": True,
            "personalized_recommendations": True,
            "certificates": True,
            "cpd_tracking": True,
            "study_groups": True,
            "custom_question_banks": True,
            "api_access": True,
            "white_label": True,
            "dedicated_support": True,
            "phone_support": True,
            "onboarding_training": True,
            "max_users": 50,  # 50 users included
            "additional_user_cost_gbp": 5.00  # £5 per additional user/month
        },
        "benefits": [
            "🏢 Everything in Professional PLUS:",
            "✅ 50 user licenses included",
            "✅ Unlimited offline banks",
            "✅ Team analytics dashboard",
            "✅ Custom question banks",
            "✅ API access for integration",
            "✅ White-label option",
            "✅ Dedicated account manager",
            "✅ Phone support",
            "✅ Onboarding & training sessions",
            "✅ Custom reporting",
            "✅ Single Sign-On (SSO) option",
            "✅ Additional users at £5/month"
        ]
    }
}

# Feature Access Control
def get_feature_access(subscription_tier: SubscriptionTier, feature: str) -> any:
    """Get feature access level for a subscription tier"""
    plan = SUBSCRIPTION_PLANS.get(subscription_tier)
    if not plan:
        return False
    return plan.get("features", {}).get(feature, False)

def can_access_specialty(subscription_tier: SubscriptionTier, specialty: str) -> bool:
    """Check if user can access a specific specialty"""
    plan = SUBSCRIPTION_PLANS.get(subscription_tier)
    if not plan:
        return False
    
    specialties = plan.get("features", {}).get("specialties_access", [])
    
    if specialties == "all":
        return True
    
    return specialty in specialties

def can_access_sector(subscription_tier: SubscriptionTier, sector: str) -> bool:
    """Check if user can access a specific sector"""
    plan = SUBSCRIPTION_PLANS.get(subscription_tier)
    if not plan:
        return False
    
    sectors = plan.get("features", {}).get("sectors_access", [])
    
    if sectors == "all":
        return True
    
    return sector in sectors

def can_access_band(subscription_tier: SubscriptionTier, band: str) -> bool:
    """Check if user can access a specific band"""
    plan = SUBSCRIPTION_PLANS.get(subscription_tier)
    if not plan:
        return False
    
    bands = plan.get("features", {}).get("bands_access", [])
    
    if bands == "all":
        return True
    
    return band in bands

def get_daily_question_limit(subscription_tier: SubscriptionTier) -> int:
    """Get daily question limit (-1 = unlimited)"""
    plan = SUBSCRIPTION_PLANS.get(subscription_tier)
    if not plan:
        return 0
    return plan.get("features", {}).get("questions_per_day", 0)

def get_offline_banks_limit(subscription_tier: SubscriptionTier) -> int:
    """Get offline banks download limit (-1 = unlimited)"""
    plan = SUBSCRIPTION_PLANS.get(subscription_tier)
    if not plan:
        return 0
    return plan.get("features", {}).get("offline_banks_limit", 0)

# Stripe Product IDs (to be created in Stripe Dashboard)
STRIPE_PRODUCTS = {
    "basic_monthly": {
        "name": "Basic Plan - Monthly",
        "price": 9.99,
        "currency": "gbp",
        "interval": "month"
    },
    "basic_annual": {
        "name": "Basic Plan - Annual",
        "price": 99.00,
        "currency": "gbp",
        "interval": "year"
    },
    "professional_monthly": {
        "name": "Professional Plan - Monthly",
        "price": 19.99,
        "currency": "gbp",
        "interval": "month"
    },
    "professional_annual": {
        "name": "Professional Plan - Annual",
        "price": 199.00,
        "currency": "gbp",
        "interval": "year"
    },
    "enterprise_monthly": {
        "name": "Enterprise Plan - Monthly",
        "price": 199.00,
        "currency": "gbp",
        "interval": "month"
    },
    "enterprise_annual": {
        "name": "Enterprise Plan - Annual",
        "price": 1999.00,
        "currency": "gbp",
        "interval": "year"
    }
}

# Webhook Events to Handle
STRIPE_WEBHOOK_EVENTS = [
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.payment_succeeded",
    "invoice.payment_failed",
    "customer.created",
    "customer.updated",
    "payment_intent.succeeded",
    "payment_intent.payment_failed"
]

