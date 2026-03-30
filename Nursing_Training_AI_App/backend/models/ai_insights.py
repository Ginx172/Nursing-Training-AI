"""
AI Insights Models - Rapoarte generate de Ollama Brain
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from core.database import Base


class AIInsight(Base):
    """Rapoarte si insights generate de Ollama orchestrator"""
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, autoincrement=True)

    report_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)

    model_used = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    generation_time_seconds = Column(Float, nullable=True)

    analysis_period_start = Column(DateTime(timezone=True), nullable=True)
    analysis_period_end = Column(DateTime(timezone=True), nullable=True)

    insights = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    raw_response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    generated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
