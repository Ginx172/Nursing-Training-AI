"""
NHS Compliance Module
Covers DTAC, DSPT, DCB0129/DCB0160 requirements for healthcare IT systems.

Standards implemented:
- DTAC (Digital Technology Assessment Criteria) - 5 core areas
- DSPT (Data Security and Protection Toolkit) v8 2025/26
- DCB0129 (Clinical Risk Management for Health IT Manufacturers)
- UK GDPR + Data Protection Act 2018
- NHS England password policy and session management
"""

import re
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum


# ========================================
# NHS PASSWORD POLICY (DSPT / Cyber Essentials aligned)
# ========================================

# Lista de parole comune interzise (subset din NCSC top breached passwords)
COMMON_PASSWORDS = {
    "password", "password1", "password123", "123456", "12345678",
    "qwerty", "abc123", "letmein", "welcome", "admin", "login",
    "nursing", "nurse123", "nhs123", "healthcare", "patient",
    "hospital", "doctor", "medical", "clinical", "band5", "band6",
}


class NHSPasswordPolicy:
    """
    Politica de parola aliniata la NHS DSPT v8 si NCSC guidance.
    - Minim 12 caractere (NCSC recomanda 12+)
    - Cel putin 1 litera mare, 1 litera mica, 1 cifra
    - Nu din lista de parole comune compromise
    - Nu contine email-ul sau username-ul
    """

    MIN_LENGTH = 12
    MAX_LENGTH = 128

    @classmethod
    def validate(cls, password: str, email: str = "", username: str = "") -> Optional[str]:
        """
        Valideaza parola contra politicii NHS.
        Returneaza None daca e valida, altfel mesajul de eroare.
        """
        if len(password) < cls.MIN_LENGTH:
            return f"Password must be at least {cls.MIN_LENGTH} characters (NHS security requirement)"

        if len(password) > cls.MAX_LENGTH:
            return f"Password must not exceed {cls.MAX_LENGTH} characters"

        if not re.search(r"[A-Z]", password):
            return "Password must contain at least one uppercase letter"

        if not re.search(r"[a-z]", password):
            return "Password must contain at least one lowercase letter"

        if not re.search(r"\d", password):
            return "Password must contain at least one digit"

        if password.lower() in COMMON_PASSWORDS:
            return "This password is too common and has been found in data breaches. Choose a stronger password."

        # Nu permite parola sa contina email/username
        if email and email.split("@")[0].lower() in password.lower():
            return "Password must not contain your email address"

        if username and len(username) > 2 and username.lower() in password.lower():
            return "Password must not contain your username"

        return None


# ========================================
# NHS SESSION POLICY
# ========================================

class NHSSessionPolicy:
    """
    Politica de sesiune aliniata la NHS DSPT.
    - Timeout inactivitate: 15 minute pentru date sensibile, 30 min general
    - Re-autentificare obligatorie pentru operatiuni critice
    - Sesiuni concurente limitate
    """
    INACTIVITY_TIMEOUT_MINUTES = 30
    SENSITIVE_OPERATION_TIMEOUT_MINUTES = 15
    MAX_CONCURRENT_SESSIONS = 3
    ACCESS_TOKEN_MAX_MINUTES = 30
    REFRESH_TOKEN_MAX_DAYS = 7


# ========================================
# NHS AUDIT REQUIREMENTS (DSPT)
# ========================================

class NHSAuditEvent(str, Enum):
    """Evenimente care TREBUIE loggate conform DSPT"""
    LOGIN_SUCCESS = "nhs.auth.login_success"
    LOGIN_FAILURE = "nhs.auth.login_failure"
    LOGOUT = "nhs.auth.logout"
    PASSWORD_CHANGE = "nhs.auth.password_change"
    ACCOUNT_LOCKOUT = "nhs.auth.account_lockout"
    DATA_ACCESS = "nhs.data.access"
    DATA_EXPORT = "nhs.data.export"
    DATA_DELETION = "nhs.data.deletion"
    ADMIN_ACTION = "nhs.admin.action"
    PERMISSION_CHANGE = "nhs.admin.permission_change"
    CLINICAL_DATA_ACCESS = "nhs.clinical.data_access"


# ========================================
# DTAC COMPLIANCE STATUS
# ========================================

class DTACArea(str, Enum):
    """Cele 5 arii DTAC"""
    CLINICAL_SAFETY = "clinical_safety"
    DATA_PROTECTION = "data_protection"
    TECHNICAL_ASSURANCE = "technical_assurance"
    INTEROPERABILITY = "interoperability"
    USABILITY_ACCESSIBILITY = "usability_accessibility"


def get_dtac_compliance_status() -> Dict[str, Any]:
    """
    Returneaza statusul de conformitate DTAC al aplicatiei.
    Acesta este un self-assessment; pentru certificare oficiala
    se completeaza formularul DTAC la NHS England.
    """
    return {
        "standard": "NHS Digital Technology Assessment Criteria (DTAC)",
        "version": "2025-26 (updated form, effective 24 Feb 2026)",
        "assessment_date": datetime.now(timezone.utc).isoformat(),
        "areas": {
            DTACArea.CLINICAL_SAFETY.value: {
                "status": "in_progress",
                "standard": "DCB0129 / DCB0160",
                "notes": "Clinical Safety Case Report required. CSO (Clinical Safety Officer) must be appointed - must be registered with NMC/GMC.",
                "requirements": [
                    {"id": "CS-01", "desc": "Clinical Safety Officer appointed", "met": False, "action": "Appoint NMC/GMC registered clinician as CSO"},
                    {"id": "CS-02", "desc": "Clinical Safety Case Report", "met": False, "action": "Create Hazard Log and Clinical Safety Case Report per DCB0129"},
                    {"id": "CS-03", "desc": "Hazard identification and risk assessment", "met": False, "action": "Conduct clinical hazard workshop"},
                    {"id": "CS-04", "desc": "Clinical risk management process documented", "met": False, "action": "Document CRM process in Clinical Safety Management System"},
                ],
            },
            DTACArea.DATA_PROTECTION.value: {
                "status": "partially_compliant",
                "standard": "UK GDPR + DPA 2018",
                "requirements": [
                    {"id": "DP-01", "desc": "Data Protection Impact Assessment (DPIA)", "met": False, "action": "Complete DPIA for personal/health data processing"},
                    {"id": "DP-02", "desc": "Privacy notice published", "met": False, "action": "Create and publish privacy notice"},
                    {"id": "DP-03", "desc": "GDPR data export (Article 15)", "met": True, "action": "Implemented: GET /api/users/me/data-export"},
                    {"id": "DP-04", "desc": "GDPR data deletion (Article 17)", "met": True, "action": "Implemented: DELETE /api/users/me/data"},
                    {"id": "DP-05", "desc": "Data encrypted at rest", "met": True, "action": "PostgreSQL encryption + Fernet field-level encryption"},
                    {"id": "DP-06", "desc": "Data encrypted in transit", "met": True, "action": "TLS required in production (HSTS header set)"},
                    {"id": "DP-07", "desc": "Data retention policy defined", "met": True, "action": "7-year healthcare data retention configured"},
                ],
            },
            DTACArea.TECHNICAL_ASSURANCE.value: {
                "status": "partially_compliant",
                "standard": "DSPT v8 / Cyber Essentials",
                "requirements": [
                    {"id": "TA-01", "desc": "Authentication with strong password policy", "met": True, "action": "NHS-grade password policy (12+ chars, complexity, common password check)"},
                    {"id": "TA-02", "desc": "Role-based access control", "met": True, "action": "RBAC with admin/trainer/student/demo roles"},
                    {"id": "TA-03", "desc": "Session management with timeout", "met": True, "action": "30-min access token, 7-day refresh, inactivity timeout"},
                    {"id": "TA-04", "desc": "Audit logging", "met": True, "action": "Security event logging to JSONL files"},
                    {"id": "TA-05", "desc": "Input validation and sanitization", "met": True, "action": "Pydantic validation + XSS/SQLi detection middleware"},
                    {"id": "TA-06", "desc": "Vulnerability management process", "met": False, "action": "Establish regular dependency scanning (pip-audit, npm audit)"},
                    {"id": "TA-07", "desc": "Penetration testing", "met": False, "action": "Commission annual penetration test"},
                    {"id": "TA-08", "desc": "Account lockout after failed attempts", "met": True, "action": "Rate limiting on login endpoint (5 per 5 minutes)"},
                ],
            },
            DTACArea.INTEROPERABILITY.value: {
                "status": "planned",
                "standard": "NHS Interoperability Standards",
                "requirements": [
                    {"id": "IO-01", "desc": "RESTful API with OpenAPI spec", "met": True, "action": "FastAPI auto-generates OpenAPI 3.0 spec"},
                    {"id": "IO-02", "desc": "FHIR compatibility", "met": False, "action": "Plan HL7 FHIR R4 support for patient data exchange"},
                    {"id": "IO-03", "desc": "NHS login integration (CIS2)", "met": False, "action": "Integrate NHS Care Identity Service 2 for SSO"},
                    {"id": "IO-04", "desc": "Standard data formats (JSON/XML)", "met": True, "action": "All APIs return JSON"},
                ],
            },
            DTACArea.USABILITY_ACCESSIBILITY.value: {
                "status": "needs_work",
                "standard": "WCAG 2.1 AA / EN 301 549",
                "requirements": [
                    {"id": "UA-01", "desc": "WCAG 2.1 Level AA compliance", "met": False, "action": "Conduct accessibility audit and remediate findings"},
                    {"id": "UA-02", "desc": "User testing with NHS staff", "met": False, "action": "Conduct usability testing with Band 5-7 nurses"},
                    {"id": "UA-03", "desc": "Mobile responsive design", "met": True, "action": "Tailwind CSS responsive layout"},
                    {"id": "UA-04", "desc": "Browser compatibility (NHS devices)", "met": True, "action": "Chrome/Edge support (primary NHS browsers)"},
                ],
            },
        },
        "overall_readiness": "in_progress",
        "next_steps": [
            "1. Appoint Clinical Safety Officer (NMC/GMC registered)",
            "2. Create Clinical Safety Case Report (DCB0129)",
            "3. Complete Data Protection Impact Assessment (DPIA)",
            "4. Publish privacy notice and terms of service",
            "5. Commission penetration test",
            "6. Conduct WCAG 2.1 AA accessibility audit",
            "7. Complete DSPT self-assessment at dsptoolkit.nhs.uk",
            "8. Submit updated DTAC form to NHS England",
        ],
    }


def get_dspt_readiness() -> Dict[str, Any]:
    """Returneaza statusul de pregatire DSPT v8"""
    return {
        "standard": "NHS Data Security and Protection Toolkit v8 (2025/26)",
        "deadline": "30 June 2026",
        "framework": "NCSC Cyber Assessment Framework (CAF) aligned",
        "key_areas": {
            "governance": {
                "data_security_lead_appointed": False,
                "information_governance_policy": False,
                "data_protection_officer": False,
            },
            "access_control": {
                "role_based_access": True,
                "strong_authentication": True,
                "password_policy_nhs_compliant": True,
                "mfa_available": False,
            },
            "data_security": {
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "audit_logging": True,
                "backup_and_recovery": False,
            },
            "incident_management": {
                "incident_response_plan": False,
                "breach_notification_process": False,
            },
            "staff_training": {
                "security_awareness_training": False,
                "data_protection_training": False,
            },
        },
        "action_required": "Complete DSPT self-assessment at https://www.dsptoolkit.nhs.uk/ before 30 June 2026",
    }


def get_dcb0129_status() -> Dict[str, Any]:
    """Returneaza statusul de conformitate DCB0129"""
    return {
        "standard": "DCB0129: Clinical Risk Management for Health IT Manufacturers",
        "legal_basis": "Health and Social Care Act 2012",
        "status": "not_started",
        "requirements": {
            "clinical_safety_officer": {
                "appointed": False,
                "requirement": "Must be a senior clinician registered with NMC, GMC, or equivalent",
            },
            "clinical_safety_management_system": {
                "documented": False,
                "requirement": "Documented process for clinical risk management",
            },
            "hazard_log": {
                "created": False,
                "requirement": "Register of identified clinical hazards with risk ratings",
            },
            "clinical_safety_case_report": {
                "created": False,
                "requirement": "Evidence that clinical risks are managed to acceptable levels",
            },
            "release_management": {
                "process_defined": False,
                "requirement": "Clinical safety assessment before each release",
            },
        },
        "note": "DCB0129 compliance is MANDATORY for placing health IT on the NHS market. A Clinical Safety Officer must be appointed before clinical deployment.",
    }
