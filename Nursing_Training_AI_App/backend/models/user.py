"""
👤 User Models pentru Nursing Training AI
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum


class UserRole(str, enum.Enum):
    """Rolurile utilizatorilor"""
    ADMIN = "admin"
    TRAINER = "trainer"
    STUDENT = "student"
    DEMO = "demo"


class NHSBand(str, enum.Enum):
    """Benzile NHS"""
    BAND_2 = "band_2"
    BAND_3 = "band_3"
    BAND_4 = "band_4"
    BAND_5 = "band_5"
    BAND_6 = "band_6"
    BAND_7 = "band_7"
    BAND_8A = "band_8a"
    BAND_8B = "band_8b"
    BAND_8C = "band_8c"
    BAND_8D = "band_8d"
    BAND_9 = "band_9"


class SubscriptionTier(str, enum.Enum):
    """Nivelurile de abonament"""
    DEMO = "demo"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class User(Base):
    """Modelul pentru utilizatori"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Informații profesionale
    nhs_band = Column(Enum(NHSBand), nullable=True)
    specialization = Column(String(100), nullable=True)
    years_experience = Column(Integer, default=0)
    
    # Abonament și acces
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.DEMO)
    subscription_expires_at = Column(DateTime, nullable=True)
    demo_questions_used = Column(Integer, default=0)
    demo_questions_limit = Column(Integer, default=3)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)

    # Two-Factor Authentication (2FA / TOTP)
    totp_secret = Column(String(64), nullable=True)
    totp_enabled = Column(Boolean, default=False)
    backup_codes = Column(Text, nullable=True)  # JSON array of hashed backup codes
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Preferințe
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    
    # Relationships
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', band='{self.nhs_band}')>"


class UserProgress(Base):
    """Modelul pentru progresul utilizatorului"""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Progres pe band
    current_band = Column(Enum(NHSBand), nullable=False)
    band_progress_percentage = Column(Integer, default=0)
    
    # Statistici
    total_questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_study_time_minutes = Column(Integer, default=0)
    
    # Competențe
    clinical_skills_score = Column(Integer, default=0)
    management_skills_score = Column(Integer, default=0)
    communication_skills_score = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="progress")

    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, band='{self.current_band}')>"


class UserSession(Base):
    """Modelul pentru sesiunile utilizatorilor"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    
    # Informații sesiune
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(50), nullable=True)  # web, mobile, desktop
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())

    # Relationship
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, active={self.is_active})>"
