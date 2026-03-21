"""
Nursing Training AI - Phase 2 Models
Specialities, Bands, Question Categories, Trusts, Interview Sessions
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    ForeignKey, Float, JSON, Enum as SAEnum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import enum


# ========================================
# ENUMS
# ========================================

class InterviewMode(str, enum.Enum):
    FULL_TEXT = "full_text"
    FULL_AUDIO = "full_audio"
    MIXED = "mixed"

class InterviewStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class DifficultyLevel(str, enum.Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# ========================================
# SPECIALITIES - NHS Departments/Wards
# ========================================

class Speciality(Base):
    __tablename__ = "specialities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    questions = relationship("InterviewQuestion", back_populates="speciality")
    interview_sessions = relationship("InterviewSession", back_populates="speciality")

    def __repr__(self):
        return f"<Speciality(code='{self.code}', name='{self.name}')>"


# ========================================
# BANDS - NHS Pay Bands with Focus Areas
# ========================================

class Band(Base):
    __tablename__ = "bands"

    id = Column(Integer, primary_key=True, index=True)
    band_number = Column(String(10), unique=True, nullable=False)  # "2", "5", "8a"
    title = Column(String(200), nullable=False)  # "Staff Nurse"
    description = Column(Text, nullable=True)
    focus_areas = Column(JSON, nullable=True)  # ["Clinical", "Patient care"]
    management_level = Column(String(50), default="none")  # none, entry, mid, senior
    min_experience_years = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    questions = relationship("InterviewQuestion", back_populates="band")
    interview_sessions = relationship("InterviewSession", back_populates="band")

    def __repr__(self):
        return f"<Band(number='{self.band_number}', title='{self.title}')>"


# ========================================
# QUESTION CATEGORIES
# ========================================

class QuestionCategory(Base):
    __tablename__ = "question_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    applies_from_band = Column(String(10), default="2")  # Minimum band
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    questions = relationship("InterviewQuestion", back_populates="category")

    def __repr__(self):
        return f"<QuestionCategory(name='{self.name}')>"


# ========================================
# INTERVIEW QUESTIONS (separate from training questions)
# ========================================

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)

    # Content
    text = Column(Text, nullable=False)
    model_answer = Column(Text, nullable=False)
    keywords = Column(JSON, nullable=True)  # ["ABCDE", "escalation", "NEWS2"]

    # Foreign Keys
    speciality_id = Column(Integer, ForeignKey("specialities.id"), nullable=True)
    band_id = Column(Integer, ForeignKey("bands.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("question_categories.id"), nullable=False)

    # Metadata
    difficulty = Column(SAEnum(DifficultyLevel), default=DifficultyLevel.INTERMEDIATE)
    max_score = Column(Integer, default=10)
    is_intro = Column(Boolean, default=False)  # Intro questions (motivation, etc.)
    is_generic = Column(Boolean, default=False)  # Applies to all specialities
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    speciality = relationship("Speciality", back_populates="questions")
    band = relationship("Band", back_populates="questions")
    category = relationship("QuestionCategory", back_populates="questions")
    trust_overrides = relationship("TrustQuestion", back_populates="question")
    interview_answers = relationship("InterviewAnswer", back_populates="question")

    def __repr__(self):
        return f"<InterviewQuestion(id={self.id}, band={self.band_id}, diff='{self.difficulty}')>"


# ========================================
# NHS TRUSTS
# ========================================

class Trust(Base):
    __tablename__ = "trusts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    region = Column(String(200), nullable=True)
    values = Column(JSON, nullable=True)  # ["Compassion", "Excellence", "Respect"]
    custom_questions_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    trust_questions = relationship("TrustQuestion", back_populates="trust")
    interview_sessions = relationship("InterviewSession", back_populates="trust")

    def __repr__(self):
        return f"<Trust(code='{self.code}', name='{self.name}')>"


# ========================================
# TRUST-SPECIFIC QUESTIONS
# ========================================

class TrustQuestion(Base):
    __tablename__ = "trust_questions"

    id = Column(Integer, primary_key=True, index=True)
    trust_id = Column(Integer, ForeignKey("trusts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=True)

    # Override or custom question
    custom_text = Column(Text, nullable=True)  # Override question text
    custom_model_answer = Column(Text, nullable=True)
    priority = Column(String(20), default="normal")  # low, normal, high, required
    is_additional = Column(Boolean, default=False)  # True = extra question, not override

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    trust = relationship("Trust", back_populates="trust_questions")
    question = relationship("InterviewQuestion", back_populates="trust_overrides")

    def __repr__(self):
        return f"<TrustQuestion(trust={self.trust_id}, question={self.question_id})>"


# ========================================
# INTERVIEW SESSIONS
# ========================================

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    speciality_id = Column(Integer, ForeignKey("specialities.id"), nullable=False)
    band_id = Column(Integer, ForeignKey("bands.id"), nullable=False)
    trust_id = Column(Integer, ForeignKey("trusts.id"), nullable=True)

    # Session config
    mode = Column(SAEnum(InterviewMode), default=InterviewMode.FULL_TEXT)
    total_questions = Column(Integer, default=10)

    # Results
    status = Column(SAEnum(InterviewStatus), default=InterviewStatus.NOT_STARTED)
    total_score = Column(Float, default=0.0)
    max_possible_score = Column(Float, default=0.0)
    score_percentage = Column(Float, default=0.0)
    passed = Column(Boolean, nullable=True)
    pass_threshold = Column(Float, default=70.0)

    # Feedback
    overall_feedback = Column(Text, nullable=True)
    strengths_summary = Column(JSON, nullable=True)
    weaknesses_summary = Column(JSON, nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")
    speciality = relationship("Speciality", back_populates="interview_sessions")
    band = relationship("Band", back_populates="interview_sessions")
    trust = relationship("Trust", back_populates="interview_sessions")
    answers = relationship("InterviewAnswer", back_populates="session")

    def __repr__(self):
        return f"<InterviewSession(user={self.user_id}, status='{self.status}')>"


# ========================================
# INTERVIEW ANSWERS
# ========================================

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)
    question_order = Column(Integer, nullable=False)

    # Answer
    user_answer = Column(Text, nullable=True)
    audio_url = Column(String(500), nullable=True)  # For audio mode

    # Scoring
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=10.0)

    # AI Feedback
    feedback = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    keywords_matched = Column(JSON, nullable=True)
    keywords_missed = Column(JSON, nullable=True)

    # Follow-up
    follow_up_question = Column(Text, nullable=True)
    follow_up_answer = Column(Text, nullable=True)
    follow_up_score = Column(Float, nullable=True)

    # Timestamps
    answered_at = Column(DateTime, default=func.now())
    time_taken_seconds = Column(Integer, nullable=True)

    # Relationships
    session = relationship("InterviewSession", back_populates="answers")
    question = relationship("InterviewQuestion", back_populates="interview_answers")

    def __repr__(self):
        return f"<InterviewAnswer(session={self.session_id}, score={self.score}/{self.max_score})>"
