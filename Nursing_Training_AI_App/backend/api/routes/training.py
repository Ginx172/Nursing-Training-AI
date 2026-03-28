"""
Training routes - session history, progress, results
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from core.database import get_db
from models.user import User
from models.training import TrainingSession, UserAnswer
from api.dependencies import get_current_active_user

router = APIRouter()


@router.get("/ping")
async def ping():
    return {"training": "ok"}


@router.get("/sessions")
async def get_training_sessions(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Lista sesiunilor de training ale utilizatorului"""
    query = db.query(TrainingSession).filter(TrainingSession.user_id == user.id)
    total = query.count()
    sessions = query.order_by(TrainingSession.started_at.desc()).offset(offset).limit(limit).all()

    return {
        "success": True,
        "sessions": [
            {
                "id": s.id,
                "session_name": s.session_name,
                "nhs_band": s.nhs_band,
                "specialization": s.specialization,
                "question_count": s.question_count,
                "total_questions": s.total_questions,
                "correct_answers": s.correct_answers,
                "score_percentage": s.score_percentage,
                "duration_minutes": s.duration_minutes,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "is_completed": s.is_completed,
                "is_demo": s.is_demo,
            }
            for s in sessions
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/sessions/{session_id}")
async def get_session_detail(
    session_id: int,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Detalii sesiune cu feedback per intrebare"""
    session = db.query(TrainingSession).filter(
        TrainingSession.id == session_id,
        TrainingSession.user_id == user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answers = db.query(UserAnswer).filter(
        UserAnswer.user_id == user.id,
    ).order_by(UserAnswer.answered_at.desc()).limit(session.total_questions or 15).all()

    return {
        "success": True,
        "session": {
            "id": session.id,
            "session_name": session.session_name,
            "nhs_band": session.nhs_band,
            "specialization": session.specialization,
            "question_count": session.question_count,
            "total_questions": session.total_questions,
            "correct_answers": session.correct_answers,
            "score_percentage": session.score_percentage,
            "duration_minutes": session.duration_minutes,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "is_completed": session.is_completed,
        },
        "answers": [
            {
                "id": a.id,
                "question_id": a.question_id,
                "user_answer": a.user_answer[:200] if a.user_answer else None,
                "is_correct": a.is_correct,
                "confidence_level": a.confidence_level,
                "time_taken_seconds": a.time_taken_seconds,
                "ai_feedback": a.ai_feedback,
                "improvement_suggestions": a.improvement_suggestions,
                "answered_at": a.answered_at.isoformat() if a.answered_at else None,
            }
            for a in answers
        ],
    }


@router.get("/summary")
async def get_training_summary(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Rezumat general al progresului de training"""
    total_sessions = db.query(func.count(TrainingSession.id)).filter(
        TrainingSession.user_id == user.id,
    ).scalar() or 0

    completed_sessions = db.query(func.count(TrainingSession.id)).filter(
        TrainingSession.user_id == user.id,
        TrainingSession.is_completed == True,
    ).scalar() or 0

    avg_score = db.query(func.avg(TrainingSession.score_percentage)).filter(
        TrainingSession.user_id == user.id,
        TrainingSession.is_completed == True,
    ).scalar()

    total_answers = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id == user.id,
    ).scalar() or 0

    correct_answers = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id == user.id,
        UserAnswer.is_correct == True,
    ).scalar() or 0

    return {
        "success": True,
        "summary": {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "average_score": round(avg_score, 1) if avg_score else 0,
            "total_answers": total_answers,
            "correct_answers": correct_answers,
            "accuracy": round(correct_answers / max(total_answers, 1) * 100, 1),
        },
    }
