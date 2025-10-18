"""
SDK Data Models
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    name: str
    nmc_number: Optional[str]
    current_band: str
    sector: str
    specialty: str
    subscription_tier: str
    created_at: str
    last_active: str

@dataclass
class Question:
    id: str
    sector: str
    specialty: str
    band: str
    question_type: str
    question_text: str
    difficulty: str
    competencies: List[str]

@dataclass
class QuestionBank:
    id: str
    sector: str
    specialty: str
    band: str
    total_questions: int
    questions: List[Question]

@dataclass
class Analytics:
    user_id: str
    questions_completed: int
    accuracy_percentage: float
    time_spent_minutes: int
    performance_by_type: Dict[str, Any]
    performance_by_specialty: Dict[str, Any]

@dataclass
class Subscription:
    id: str
    user_id: str
    tier: str
    status: str
    amount_gbp: float
    next_billing_date: str

