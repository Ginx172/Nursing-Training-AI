"""
Learning Profile Models - Profil de invatare per user + evenimente
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from core.database import Base


class UserLearningProfile(Base):
    """Profil agregat de invatare per user - baseline, trend, strengths/weaknesses"""
    __tablename__ = "user_learning_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Baseline (primele 20 raspunsuri)
    baseline_accuracy_pct = Column(Float, nullable=True)
    baseline_established_at = Column(DateTime(timezone=True), nullable=True)
    baseline_questions = Column(Integer, default=0)

    # Current performance (rolling)
    current_accuracy_pct = Column(Float, default=0.0)
    total_questions_answered = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)

    # Strengths / Weaknesses
    strongest_specialty = Column(String(100), nullable=True)
    weakest_specialty = Column(String(100), nullable=True)
    strongest_competency = Column(String(100), nullable=True)
    weakest_competency = Column(String(100), nullable=True)

    # Specialty performance breakdown (JSON: {"amu": 85.2, "emergency": 72.1, ...})
    specialty_scores = Column(JSON, nullable=True)
    # Competency breakdown (JSON: {"clinical": 4.2, "management": 3.1, ...})
    competency_scores = Column(JSON, nullable=True)

    # Trend
    trend = Column(String(20), default="stable")  # improving, stable, declining
    learning_velocity = Column(Float, default=0.0)  # answers per day average

    # Recommendations
    last_recommendation_at = Column(DateTime(timezone=True), nullable=True)
    recommendations = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LearningEvent(Base):
    """Evenimente granulare de invatare"""
    __tablename__ = "learning_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    event_type = Column(String(50), nullable=False, index=True)
    # Types: answer, session_start, session_complete, recommendation_viewed, recommendation_dismissed

    question_id = Column(Integer, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)

    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index('ix_learning_events_user_type', 'user_id', 'event_type'),
        Index('ix_learning_events_user_date', 'user_id', 'created_at'),
    )
