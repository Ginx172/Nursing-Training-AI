"""
📚 Training Models pentru Nursing Training AI
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class QuestionType(str, enum.Enum):
    """Tipurile de întrebări"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    CALCULATION = "calculation"
    SCENARIO = "scenario"
    CASE_STUDY = "case_study"


class DifficultyLevel(str, enum.Enum):
    """Nivelurile de dificultate"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Question(Base):
    """Modelul pentru întrebări"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Conținut
    title = Column(String(500), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    
    # Opțiuni pentru multiple choice
    options = Column(JSON, nullable=True)  # Lista de opțiuni
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    
    # Metadate
    nhs_band = Column(String(20), nullable=False)  # band_6, band_7, etc.
    specialization = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)  # Lista de tag-uri
    
    # Calculări (pentru întrebări de calcul)
    calculation_formula = Column(Text, nullable=True)
    calculation_units = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relații
    answers = relationship("UserAnswer", back_populates="question")
    
    def __repr__(self):
        return f"<Question(id={self.id}, type='{self.question_type}', band='{self.nhs_band}')>"


class UserAnswer(Base):
    """Modelul pentru răspunsurile utilizatorilor"""
    __tablename__ = "user_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Răspuns
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    confidence_level = Column(Integer, nullable=True)  # 1-5 scale
    
    # Timp de răspuns
    time_taken_seconds = Column(Integer, nullable=True)
    
    # Feedback
    ai_feedback = Column(Text, nullable=True)
    improvement_suggestions = Column(Text, nullable=True)
    
    # Timestamps
    answered_at = Column(DateTime, default=func.now())
    
    # Relații
    question = relationship("Question", back_populates="answers")
    
    def __repr__(self):
        return f"<UserAnswer(user_id={self.user_id}, correct={self.is_correct})>"


class TrainingSession(Base):
    """Modelul pentru sesiunile de training"""
    __tablename__ = "training_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Configurare sesiune
    session_name = Column(String(200), nullable=True)
    nhs_band = Column(String(20), nullable=False)
    specialization = Column(String(100), nullable=True)
    question_count = Column(Integer, default=10)
    
    # Rezultate
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    score_percentage = Column(Float, default=0.0)
    
    # Timp
    duration_minutes = Column(Integer, default=0)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_demo = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<TrainingSession(user_id={self.user_id}, band='{self.nhs_band}')>"


class LearningPath(Base):
    """Modelul pentru căile de învățare"""
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informații de bază
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    nhs_band = Column(String(20), nullable=False)
    specialization = Column(String(100), nullable=True)
    
    # Structură
    modules = Column(JSON, nullable=True)  # Lista de module
    prerequisites = Column(JSON, nullable=True)  # Prerechizite
    
    # Metadate
    estimated_hours = Column(Integer, default=0)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LearningPath(name='{self.name}', band='{self.nhs_band}')>"


class UserLearningPath(Base):
    """Modelul pentru progresul utilizatorului pe căile de învățare"""
    __tablename__ = "user_learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    
    # Progres
    current_module = Column(Integer, default=0)
    completed_modules = Column(JSON, nullable=True)  # Lista modulelor completate
    progress_percentage = Column(Float, default=0.0)
    
    # Timp
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_paused = Column(Boolean, default=False)
    
    # Relații
    learning_path = relationship("LearningPath")
    
    def __repr__(self):
        return f"<UserLearningPath(user_id={self.user_id}, progress={self.progress_percentage}%)>"
