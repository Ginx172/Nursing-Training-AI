"""
Two-Factor Authentication (2FA) endpoints.
TOTP-based using Google Authenticator / Authy / any TOTP app.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from core.totp import (
    generate_totp_secret, get_totp_uri, generate_qr_code_base64,
    verify_totp_code, generate_backup_codes,
)
from core.auth import hash_password, verify_password
from models.user import User
from api.dependencies import get_current_active_user

router = APIRouter()


class Enable2FAResponse(BaseModel):
    secret: str
    qr_code_base64: str
    otpauth_uri: str
    backup_codes: list


class Verify2FARequest(BaseModel):
    code: str


class Disable2FARequest(BaseModel):
    password: str
    code: str


# ========================================
# SETUP 2FA
# ========================================

@router.post("/setup", response_model=Enable2FAResponse)
async def setup_2fa(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Genereaza un secret TOTP si QR code pentru setup in authenticator app.
    NU activeaza 2FA inca - trebuie confirmat cu /verify.
    """
    if user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled. Disable it first to reconfigure.",
        )

    # Genereaza secret nou
    secret = generate_totp_secret()
    uri = get_totp_uri(secret, user.email)
    qr_base64 = generate_qr_code_base64(uri)

    # Genereaza backup codes
    backup_codes = generate_backup_codes(8)

    # Salveaza secret-ul temporar (neactivat inca)
    user.totp_secret = secret
    # Salveaza backup codes hasuite
    user.backup_codes = json.dumps([hash_password(c) for c in backup_codes])
    db.commit()

    return Enable2FAResponse(
        secret=secret,
        qr_code_base64=qr_base64,
        otpauth_uri=uri,
        backup_codes=backup_codes,  # Afisate O SINGURA DATA
    )


# ========================================
# VERIFY & ACTIVATE 2FA
# ========================================

@router.post("/verify")
async def verify_and_enable_2fa(
    data: Verify2FARequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Confirma ca utilizatorul a setat corect authenticator app-ul
    prin verificarea unui cod TOTP. Activeaza 2FA daca codul e valid.
    """
    if user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled.",
        )

    if not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Call /setup first to generate a TOTP secret.",
        )

    if not verify_totp_code(user.totp_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code. Make sure your authenticator app is synced.",
        )

    user.totp_enabled = True
    db.commit()

    return {
        "success": True,
        "message": "Two-factor authentication enabled successfully. Keep your backup codes safe.",
    }


# ========================================
# CHECK 2FA STATUS
# ========================================

@router.get("/status")
async def get_2fa_status(user: User = Depends(get_current_active_user)):
    """Returneaza statusul 2FA al utilizatorului."""
    return {
        "enabled": user.totp_enabled,
        "has_secret": user.totp_secret is not None,
    }


# ========================================
# DISABLE 2FA
# ========================================

@router.post("/disable")
async def disable_2fa(
    data: Disable2FARequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Dezactiveaza 2FA. Necesita parola + cod TOTP valid pentru confirmare.
    """
    if not user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled.",
        )

    # Verifica parola
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password.",
        )

    # Verifica TOTP cod
    if not verify_totp_code(user.totp_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code.",
        )

    user.totp_enabled = False
    user.totp_secret = None
    user.backup_codes = None
    db.commit()

    return {
        "success": True,
        "message": "Two-factor authentication disabled.",
    }
