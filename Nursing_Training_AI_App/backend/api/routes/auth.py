"""
Authentication routes - register, login, token refresh, logout, profile
"""

import threading
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.database import get_db
from core.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from core.config import settings
from core.nhs_compliance import NHSPasswordPolicy
from core.rate_limiter import rate_limit
from models.user import User, UserRole, NHSBand, SubscriptionTier
from api.schemas.auth import (
    UserRegister, UserLogin, RefreshTokenRequest,
    ChangePasswordRequest, TokenResponse, UserResponse, MessageResponse,
)
from api.dependencies import get_current_active_user

# Dummy hash pentru timing-safe login (previne timing attacks)
_DUMMY_HASH = hash_password("dummy-password-for-timing-safety")

# Token blacklist (in-memory, se pierde la restart - productie: foloseste Redis)
_blacklisted_tokens: set = set()
_blacklist_lock = threading.Lock()

router = APIRouter()


def _build_token_response(user: User) -> dict:
    """Construieste raspunsul cu token-uri pentru un utilizator"""
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


# ========================================
# HEALTH CHECK
# ========================================

@router.get("/ping")
async def ping():
    return {"auth": "ok"}


# ========================================
# REGISTER
# ========================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    db: Session = Depends(get_db),
    _rl=Depends(rate_limit(3, 300, "register")),
):
    """Inregistreaza un utilizator nou si returneaza token-uri JWT"""

    # Validare parola conform NHS DSPT password policy
    password_error = NHSPasswordPolicy.validate(data.password, email=data.email, username=data.username)
    if password_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=password_error)

    # Validare NHS band daca e furnizat
    nhs_band = None
    if data.nhs_band:
        try:
            nhs_band = NHSBand(data.nhs_band)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid NHS band. Valid values: {[b.value for b in NHSBand]}",
            )

    user = User(
        email=data.email.lower(),
        username=data.username.lower(),
        hashed_password=hash_password(data.password),
        first_name=data.first_name.strip(),
        last_name=data.last_name.strip(),
        nhs_band=nhs_band,
        specialization=data.specialization,
        role=UserRole.STUDENT,
        subscription_tier=SubscriptionTier.DEMO,
        is_active=True,
        is_verified=False,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration failed. Please try a different email or username.",
        )

    return _build_token_response(user)


# ========================================
# LOGIN
# ========================================

@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    db: Session = Depends(get_db),
    _rl=Depends(rate_limit(5, 300, "login")),
):
    """Autentifica un utilizator si returneaza token-uri JWT"""

    user = db.query(User).filter(User.email == data.email.lower()).first()

    # Timing-safe: ruleaza INTOTDEAUNA bcrypt, chiar daca user nu exista.
    # Previne timing attacks care dezvaluie daca email-ul exista.
    stored_hash = user.hashed_password if user else _DUMMY_HASH
    password_valid = verify_password(data.password, stored_hash)

    if user is None or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact support.",
        )

    # Verificare 2FA daca e activat
    if user.totp_enabled:
        if not data.totp_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="2FA code required. Please provide your authenticator code.",
                headers={"X-2FA-Required": "true"},
            )
        from core.totp import verify_totp_code
        if not verify_totp_code(user.totp_secret, data.totp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA code.",
            )

    # Actualizare last_login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    return _build_token_response(user)


# ========================================
# TOKEN REFRESH
# ========================================

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Reimprospatare access token folosind un refresh token valid"""

    payload = verify_token(data.refresh_token, expected_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated",
        )

    return _build_token_response(user)


# ========================================
# LOGOUT
# ========================================

@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, user: User = Depends(get_current_active_user)):
    """Logout - invalideaza token-ul curent prin blacklist."""
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        with _blacklist_lock:
            _blacklisted_tokens.add(token)
    return MessageResponse(success=True, message="Logged out successfully")


# ========================================
# GET CURRENT USER
# ========================================

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_active_user)):
    """Returneaza informatiile utilizatorului autentificat"""
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        nhs_band=user.nhs_band.value if user.nhs_band else None,
        specialization=user.specialization,
        years_experience=user.years_experience,
        subscription_tier=user.subscription_tier.value if user.subscription_tier else "demo",
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login,
    )


# ========================================
# CHANGE PASSWORD
# ========================================

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Schimba parola utilizatorului autentificat"""

    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    password_error = NHSPasswordPolicy.validate(data.new_password, email=user.email, username=user.username)
    if password_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=password_error)

    user.hashed_password = hash_password(data.new_password)
    db.commit()

    return MessageResponse(success=True, message="Password changed successfully")
