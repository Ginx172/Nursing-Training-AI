"""
Authentication routes - register, login, token refresh, logout, profile
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.database import get_db
from core.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from core.config import settings
from models.user import User, UserRole, NHSBand, SubscriptionTier
from api.schemas.auth import (
    UserRegister, UserLogin, RefreshTokenRequest,
    ChangePasswordRequest, TokenResponse, UserResponse, MessageResponse,
)
from api.dependencies import get_current_active_user

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
async def register(data: UserRegister, db: Session = Depends(get_db)):
    """Inregistreaza un utilizator nou si returneaza token-uri JWT"""

    # Validare parola (minim o litera mare, o cifra)
    if not any(c.isupper() for c in data.password) or not any(c.isdigit() for c in data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter and one digit",
        )

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
            detail="Email or username already registered",
        )

    return _build_token_response(user)


# ========================================
# LOGIN
# ========================================

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Autentifica un utilizator si returneaza token-uri JWT"""

    user = db.query(User).filter(User.email == data.email.lower()).first()

    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact support.",
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
async def logout(user: User = Depends(get_current_active_user)):
    """
    Logout - invalideaza sesiunea curenta.
    Nota: Cu JWT stateless, clientul sterge token-ul local.
    Pentru blacklist server-side, e necesara integrare Redis.
    """
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

    if not any(c.isupper() for c in data.new_password) or not any(c.isdigit() for c in data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must contain at least one uppercase letter and one digit",
        )

    user.hashed_password = hash_password(data.new_password)
    db.commit()

    return MessageResponse(success=True, message="Password changed successfully")
