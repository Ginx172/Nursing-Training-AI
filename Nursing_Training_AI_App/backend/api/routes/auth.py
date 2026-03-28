"""
Authentication routes - register, login, token refresh, logout, profile
"""

import hashlib
import threading
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.database import get_db, SessionLocal
from core.auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    verify_token, create_password_reset_token, create_email_verification_token,
)
from core.config import settings
from core.nhs_compliance import NHSPasswordPolicy
from core.rate_limiter import rate_limit
from models.user import User, UserRole, NHSBand, SubscriptionTier
from api.schemas.auth import (
    UserRegister, UserLogin, RefreshTokenRequest,
    ChangePasswordRequest, PasswordResetRequest, PasswordResetConfirm,
    TokenResponse, UserResponse, MessageResponse,
)
from api.dependencies import get_current_active_user

# Dummy hash pentru timing-safe login (previne timing attacks)
_DUMMY_HASH = hash_password("dummy-password-for-timing-safety")

# Token blacklist - in-memory set ca hot cache, backed by PostgreSQL
_blacklisted_tokens: set = set()  # stocheaza token_hash (SHA-256)
_blacklist_lock = threading.Lock()


def _hash_token(token: str) -> str:
    """SHA-256 hash al JWT-ului pentru stocare sigura"""
    return hashlib.sha256(token.encode()).hexdigest()


def load_blacklist_from_db():
    """Incarca token-urile revocate din DB la startup"""
    try:
        db = SessionLocal()
        try:
            from models.security import TokenBlacklist
            active = db.query(TokenBlacklist.token_hash).filter(
                TokenBlacklist.expires_at > datetime.now(timezone.utc)
            ).all()
            with _blacklist_lock:
                for (th,) in active:
                    _blacklisted_tokens.add(th)
            print(f"Loaded {len(active)} blacklisted tokens from DB")
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: could not load token blacklist from DB: {e}")


def cleanup_expired_tokens():
    """Sterge token-urile expirate din DB si din cache"""
    try:
        db = SessionLocal()
        try:
            from models.security import TokenBlacklist
            deleted = db.query(TokenBlacklist).filter(
                TokenBlacklist.expires_at <= datetime.now(timezone.utc)
            ).delete()
            db.commit()
            if deleted:
                print(f"Cleaned up {deleted} expired blacklisted tokens")
        finally:
            db.close()
    except Exception:
        pass

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
            detail="Registration could not be completed. Please try again.",
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
    """Logout - invalideaza token-ul curent prin blacklist persistent."""
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        token_hash = _hash_token(token)

        # Persist in DB
        try:
            payload = verify_token(token, expected_type="access")
            exp_timestamp = payload.get("exp") if payload else None
            if exp_timestamp:
                expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            else:
                expires_at = datetime.now(timezone.utc)

            db = SessionLocal()
            try:
                from models.security import TokenBlacklist
                record = TokenBlacklist(
                    token_hash=token_hash,
                    user_id=user.id,
                    expires_at=expires_at,
                )
                db.add(record)
                db.commit()
            except IntegrityError:
                db.rollback()  # token deja in blacklist
            finally:
                db.close()
        except Exception:
            pass  # DB write failed, in-memory cache still works

        # Hot cache update
        with _blacklist_lock:
            _blacklisted_tokens.add(token_hash)

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


# ========================================
# FORGOT PASSWORD / RESET PASSWORD
# ========================================

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
    _rl=Depends(rate_limit(3, 300, "forgot_password")),
):
    """Trimite email cu link de reset parola. Raspuns identic indiferent daca email-ul exista."""
    user = db.query(User).filter(User.email == data.email.lower()).first()

    if user and user.is_active:
        token = create_password_reset_token({"sub": str(user.id), "email": user.email})
        frontend_url = settings.FRONTEND_URL if hasattr(settings, "FRONTEND_URL") else "http://localhost:3000"
        reset_link = f"{frontend_url}/reset-password?token={token}"

        from services.email_service import email_service
        await email_service.send_email(
            to_email=user.email,
            subject="Password Reset - Nursing Training AI",
            html_content=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #4F46E5;">Password Reset Request</h2>
                <p>Hello {user.first_name},</p>
                <p>We received a request to reset your password. Click the button below to set a new password:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}"
                       style="background: #4F46E5; color: white; padding: 12px 32px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        Reset Password
                    </a>
                </p>
                <p style="color: #6B7280; font-size: 14px;">This link expires in 1 hour. If you did not request this, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 24px 0;">
                <p style="color: #9CA3AF; font-size: 12px;">Nursing Training AI - NHS Healthcare Training Platform</p>
            </div>
            """,
        )

    # Raspuns identic pentru a preveni account enumeration
    return MessageResponse(
        success=True,
        message="If an account with this email exists, a password reset link has been sent.",
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: PasswordResetConfirm,
    db: Session = Depends(get_db),
    _rl=Depends(rate_limit(5, 300, "reset_password")),
):
    """Reseteaza parola folosind un token valid din email"""
    payload = verify_token(data.token, expected_type="password_reset")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token. Please request a new one.",
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token. Please request a new one.",
        )

    password_error = NHSPasswordPolicy.validate(data.new_password, email=user.email, username=user.username)
    if password_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=password_error)

    user.hashed_password = hash_password(data.new_password)
    db.commit()

    return MessageResponse(success=True, message="Password has been reset successfully. You can now log in.")


# ========================================
# EMAIL VERIFICATION
# ========================================

@router.post("/send-verification", response_model=MessageResponse)
async def send_verification_email(
    user: User = Depends(get_current_active_user),
    _rl=Depends(rate_limit(2, 300, "send_verification")),
):
    """Trimite email de verificare utilizatorului autentificat"""
    if user.is_verified:
        return MessageResponse(success=True, message="Email is already verified.")

    token = create_email_verification_token({"sub": str(user.id), "email": user.email})
    frontend_url = settings.FRONTEND_URL if hasattr(settings, "FRONTEND_URL") else "http://localhost:3000"
    verify_link = f"{frontend_url}/verify-email?token={token}"

    from services.email_service import email_service
    await email_service.send_email(
        to_email=user.email,
        subject="Verify Your Email - Nursing Training AI",
        html_content=f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #4F46E5;">Verify Your Email Address</h2>
            <p>Hello {user.first_name},</p>
            <p>Please verify your email address by clicking the button below:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{verify_link}"
                   style="background: #4F46E5; color: white; padding: 12px 32px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Verify Email
                </a>
            </p>
            <p style="color: #6B7280; font-size: 14px;">This link expires in 24 hours.</p>
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 24px 0;">
            <p style="color: #9CA3AF; font-size: 12px;">Nursing Training AI - NHS Healthcare Training Platform</p>
        </div>
        """,
    )

    return MessageResponse(success=True, message="Verification email sent. Please check your inbox.")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: Session = Depends(get_db),
):
    """Verifica email-ul utilizatorului folosind token-ul din link"""
    payload = verify_token(token, expected_type="email_verification")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token.",
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token.",
        )

    if user.is_verified:
        return MessageResponse(success=True, message="Email is already verified.")

    user.is_verified = True
    db.commit()

    return MessageResponse(success=True, message="Email verified successfully!")
