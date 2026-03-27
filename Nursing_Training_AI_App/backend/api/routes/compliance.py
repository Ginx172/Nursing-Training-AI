"""
NHS Compliance and Regulatory Endpoints
Expune statusul de conformitate cu standardele NHS:
- DTAC (Digital Technology Assessment Criteria)
- DSPT v8 (Data Security and Protection Toolkit)
- DCB0129 (Clinical Risk Management)
"""

from fastapi import APIRouter, Depends
from models.user import User
from api.dependencies import get_current_admin
from core.nhs_compliance import (
    get_dtac_compliance_status,
    get_dspt_readiness,
    get_dcb0129_status,
)

router = APIRouter()


@router.get("/status")
async def get_compliance_overview(admin: User = Depends(get_current_admin)):
    """
    Returneaza statusul complet de conformitate NHS.
    Acoperire: DTAC, DSPT v8, DCB0129.
    Doar admin poate vedea acest raport.
    """
    return {
        "success": True,
        "compliance": {
            "dtac": get_dtac_compliance_status(),
            "dspt": get_dspt_readiness(),
            "dcb0129": get_dcb0129_status(),
        },
    }


@router.get("/dtac")
async def get_dtac_status(admin: User = Depends(get_current_admin)):
    """DTAC self-assessment status"""
    return {"success": True, "dtac": get_dtac_compliance_status()}


@router.get("/dspt")
async def get_dspt_status(admin: User = Depends(get_current_admin)):
    """DSPT v8 readiness status"""
    return {"success": True, "dspt": get_dspt_readiness()}


@router.get("/dcb0129")
async def get_dcb0129(admin: User = Depends(get_current_admin)):
    """DCB0129 Clinical Safety status"""
    return {"success": True, "dcb0129": get_dcb0129_status()}


@router.get("/privacy-notice")
async def get_privacy_notice():
    """
    Privacy notice publica - conform UK GDPR Article 13/14.
    Aceasta ruta este publica (fara auth) deoarece orice utilizator
    trebuie sa poata vedea privacy notice inainte de inregistrare.
    """
    return {
        "controller": "Nursing Training AI",
        "purpose": "Providing healthcare professional training services using AI-powered evaluation",
        "legal_basis": [
            "Consent (Article 6(1)(a) UK GDPR) - for account registration",
            "Contract performance (Article 6(1)(b)) - for subscription services",
            "Legitimate interest (Article 6(1)(f)) - for platform security and improvement",
        ],
        "data_categories": [
            "Identity data (name, email, NMC number)",
            "Professional data (NHS band, specialization, experience)",
            "Training data (answers, scores, progress)",
            "Technical data (IP address, browser, session data)",
            "Subscription data (tier, payment status)",
        ],
        "data_recipients": [
            "Platform internal systems",
            "Stripe (payment processing) - if subscribed",
            "Cloud hosting provider (encrypted storage)",
        ],
        "retention_period": "7 years for healthcare training records, as required by healthcare data retention regulations",
        "your_rights": {
            "access": "GET /api/users/me/data-export",
            "erasure": "DELETE /api/users/me/data",
            "rectification": "PUT /api/users/me/profile",
            "portability": "GET /api/users/me/data-export (JSON format)",
            "complaint": "You can lodge a complaint with the ICO (Information Commissioner's Office) at https://ico.org.uk",
        },
        "contact": {
            "data_protection_queries": "Contact the platform administrator",
            "ico": "https://ico.org.uk/make-a-complaint/",
        },
        "last_updated": "2026-03-27",
    }
