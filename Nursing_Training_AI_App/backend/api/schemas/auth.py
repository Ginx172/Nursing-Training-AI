"""
Pydantic schemas for authentication endpoints
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ========================================
# REQUEST SCHEMAS
# ========================================

class UserRegister(BaseModel):
    """Schema pentru inregistrare utilizator nou"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    nhs_band: Optional[str] = None
    specialization: Optional[str] = None


class UserLogin(BaseModel):
    """Schema pentru login"""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema pentru refresh token"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Schema pentru schimbare parola"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordResetRequest(BaseModel):
    """Schema pentru cerere de reset parola"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema pentru confirmare reset parola"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


# ========================================
# RESPONSE SCHEMAS
# ========================================

class TokenResponse(BaseModel):
    """Schema pentru raspuns cu token-uri"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """Schema pentru informatii utilizator"""
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    nhs_band: Optional[str] = None
    specialization: Optional[str] = None
    years_experience: int = 0
    subscription_tier: str = "demo"
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Schema pentru actualizare profil"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    nhs_band: Optional[str] = None
    specialization: Optional[str] = None
    years_experience: Optional[int] = Field(None, ge=0)
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None


class MessageResponse(BaseModel):
    """Schema generic pentru raspunsuri cu mesaj"""
    success: bool
    message: str
