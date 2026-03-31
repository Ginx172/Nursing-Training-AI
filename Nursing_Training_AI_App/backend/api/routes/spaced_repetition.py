"""
Spaced Repetition API Routes - Adaptive question selection for users
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from models.user import User
from api.dependencies import get_current_active_user
from services.spaced_repetition_service import spaced_repetition

router = APIRouter(tags=["spaced-repetition"])


@router.get("/next-questions")
async def get_next_questions(
    count: int = Query(10, ge=1, le=50),
    specialty: Optional[str] = Query(None),
    band: Optional[str] = Query(None),
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Urmatoarele intrebari optime pentru user (spaced repetition)"""
    questions = spaced_repetition.get_next_questions(
        db, user.id, count=count, specialty=specialty, band=band
    )
    return {"success": True, "questions": questions, "total": len(questions)}


@router.get("/session-plan")
async def get_session_plan(
    length: int = Query(10, ge=5, le=50),
    specialty: Optional[str] = Query(None),
    band: Optional[str] = Query(None),
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Plan de sesiune cu mix optimal de intrebari"""
    plan = spaced_repetition.get_session_plan(
        db, user.id, session_length=length, specialty=specialty, band=band
    )
    return {"success": True, **plan}
