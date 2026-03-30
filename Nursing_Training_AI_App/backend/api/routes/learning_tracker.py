"""
Learning Tracker API Routes
Endpoint-uri pentru profilul de invatare al user-ului curent.
"""

from fastapi import APIRouter, Depends, Query, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from models.user import User
from models.training import UserAnswer
from api.dependencies import get_current_active_user
from services.learning_tracker_service import learning_tracker


class SubmitAnswerRequest(BaseModel):
    question_id: int
    user_answer: str
    is_correct: bool
    time_taken_seconds: Optional[int] = None
    confidence_level: Optional[int] = None

router = APIRouter(tags=["learning-tracker"])


@router.get("/profile")
async def get_my_profile(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Profilul de invatare al user-ului curent"""
    profile = learning_tracker.get_user_profile(db, user.id)
    return {"success": True, **profile}


@router.get("/timeline")
async def get_my_timeline(
    days: int = Query(90, ge=7, le=365),
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Timeline saptamanal al progresului - pt grafice"""
    timeline = learning_tracker.get_progress_timeline(db, user.id, days)
    return {"success": True, "data": timeline, "period_days": days}


@router.get("/recommendations")
async def get_my_recommendations(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Recomandari personalizate bazate pe slabiciunile reale"""
    recommendations = learning_tracker.generate_recommendations(db, user.id)
    return {"success": True, "recommendations": recommendations, "total": len(recommendations)}


@router.post("/submit-answer")
async def submit_answer(
    data: SubmitAnswerRequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Salveaza un raspuns si actualizeaza profilul de invatare"""
    # Salveaza in UserAnswer
    answer = UserAnswer(
        user_id=user.id,
        question_id=data.question_id,
        user_answer=data.user_answer,
        is_correct=data.is_correct,
        time_taken_seconds=data.time_taken_seconds,
        confidence_level=data.confidence_level,
    )
    db.add(answer)
    db.flush()

    # Actualizeaza learning profile
    learning_tracker.record_answer(
        db, user.id, data.question_id, data.is_correct, data.time_taken_seconds
    )

    return {"success": True, "answer_id": answer.id, "message": "Answer recorded and profile updated"}


@router.post("/event")
async def record_learning_event(
    event_type: str = Query(...),
    metadata: Optional[str] = Query(None),
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Inregistreaza un eveniment de invatare"""
    import json
    meta = json.loads(metadata) if metadata else None
    learning_tracker.record_event(db, user.id, event_type, meta)
    return {"success": True, "message": "Event recorded"}
