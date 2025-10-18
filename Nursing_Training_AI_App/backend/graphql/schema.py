"""
GraphQL Schema for Nursing Training AI
Provides GraphQL API as alternative to REST for Enterprise clients
"""

import strawberry
from typing import List, Optional
from datetime import datetime

# ========================================
# TYPES
# ========================================

@strawberry.type
class User:
    id: str
    email: str
    name: str
    nmc_number: Optional[str]
    current_band: str
    sector: str
    specialty: str
    subscription_tier: str
    created_at: datetime
    last_active: datetime

@strawberry.type
class Question:
    id: str
    sector: str
    specialty: str
    band: str
    question_type: str
    question_text: str
    difficulty: str
    competencies: List[str]
    created_date: datetime

@strawberry.type
class QuestionBank:
    id: str
    sector: str
    specialty: str
    band: str
    bank_number: int
    total_questions: int
    questions: List[Question]

@strawberry.type
class UserProgress:
    user_id: str
    questions_completed: int
    accuracy: float
    streak_current: int
    streak_longest: int
    progress_to_next_band: float
    strengths: List[str]
    weaknesses: List[str]

@strawberry.type
class Analytics:
    user_id: str
    period_from: datetime
    period_to: datetime
    questions_completed: int
    accuracy_percentage: float
    time_spent_minutes: int
    performance_by_type: str  # JSON string
    performance_by_specialty: str  # JSON string

@strawberry.type
class Subscription:
    id: str
    user_id: str
    tier: str
    status: str
    billing_cycle: str
    amount_gbp: float
    next_billing_date: datetime
    cancel_at_period_end: bool

@strawberry.type
class Organization:
    id: str
    name: str
    sector: str
    subscription_tier: str
    total_members: int
    sso_enabled: bool
    created_at: datetime

# ========================================
# QUERIES
# ========================================

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: str) -> Optional[User]:
        """Get user by ID"""
        # TODO: Fetch from database
        return None
    
    @strawberry.field
    def users(self, limit: int = 10, offset: int = 0) -> List[User]:
        """Get list of users (Admin only)"""
        # TODO: Fetch from database
        return []
    
    @strawberry.field
    def question_bank(
        self,
        sector: str,
        specialty: str,
        band: str,
        bank_number: int
    ) -> Optional[QuestionBank]:
        """Get specific question bank"""
        # TODO: Fetch from database
        return None
    
    @strawberry.field
    def question_banks(
        self,
        sector: Optional[str] = None,
        specialty: Optional[str] = None,
        band: Optional[str] = None,
        limit: int = 10
    ) -> List[QuestionBank]:
        """Search question banks"""
        # TODO: Fetch from database with filters
        return []
    
    @strawberry.field
    def user_progress(self, user_id: str) -> Optional[UserProgress]:
        """Get user progress"""
        # TODO: Fetch from database
        return None
    
    @strawberry.field
    def user_analytics(
        self,
        user_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Optional[Analytics]:
        """Get user analytics"""
        # TODO: Fetch from analytics service
        return None
    
    @strawberry.field
    def organization(self, id: str) -> Optional[Organization]:
        """Get organization details (Admin only)"""
        # TODO: Fetch from database
        return None

# ========================================
# MUTATIONS
# ========================================

@strawberry.input
class CreateUserInput:
    email: str
    name: str
    password: str
    current_band: str
    sector: str
    specialty: str

@strawberry.input
class UpdateUserInput:
    name: Optional[str] = None
    current_band: Optional[str] = None
    sector: Optional[str] = None
    specialty: Optional[str] = None

@strawberry.input
class AnswerQuestionInput:
    question_id: str
    answer: str
    time_taken_seconds: int

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input: CreateUserInput) -> User:
        """Create new user"""
        # TODO: Create user in database
        raise NotImplementedError()
    
    @strawberry.mutation
    def update_user(self, user_id: str, input: UpdateUserInput) -> User:
        """Update user information"""
        # TODO: Update database
        raise NotImplementedError()
    
    @strawberry.mutation
    def delete_user(self, user_id: str) -> bool:
        """Delete user (GDPR right to erasure)"""
        # TODO: Delete from database
        return False
    
    @strawberry.mutation
    def answer_question(self, user_id: str, input: AnswerQuestionInput) -> UserProgress:
        """Submit answer to question"""
        # TODO: Save answer and update progress
        raise NotImplementedError()
    
    @strawberry.mutation
    def create_subscription(
        self,
        user_id: str,
        tier: str,
        billing_cycle: str
    ) -> Subscription:
        """Create new subscription"""
        # TODO: Create in Stripe and database
        raise NotImplementedError()

# ========================================
# SUBSCRIPTIONS (Real-time)
# ========================================

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def progress_updates(self, user_id: str) -> UserProgress:
        """Subscribe to real-time progress updates"""
        # TODO: Implement WebSocket subscription
        yield None

# ========================================
# SCHEMA
# ========================================

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # subscription=Subscription  # Enable when implementing WebSockets
)

