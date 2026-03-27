"""
Dashboard statistics endpoint - real data from DB
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.database import get_db
from models.user import User, UserProgress
from models.training import Question, UserAnswer, TrainingSession
from api.dependencies import get_current_active_user

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Returneaza statistici reale pentru dashboard.
    Datele vin din DB, nu sunt hardcoded.
    """
    # Statistici globale
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    total_questions_in_db = db.query(func.count(Question.id)).filter(Question.is_active == True).scalar() or 0
    total_answers = db.query(func.count(UserAnswer.id)).scalar() or 0
    total_sessions = db.query(func.count(TrainingSession.id)).scalar() or 0

    # Acuratete medie globala
    total_correct = db.query(func.sum(UserProgress.correct_answers)).scalar() or 0
    total_attempted = db.query(func.sum(UserProgress.total_questions_answered)).scalar() or 0
    avg_competency = round(total_correct / max(total_attempted, 1) * 100, 1)

    # Sesiuni completate azi
    from datetime import datetime, timezone
    from sqlalchemy import cast, Date
    today = datetime.now(timezone.utc).date()
    sessions_today = db.query(func.count(TrainingSession.id)).filter(
        cast(TrainingSession.started_at, Date) == today
    ).scalar() or 0

    # Statistici personale ale utilizatorului curent
    my_progress = db.query(UserProgress).filter(UserProgress.user_id == user.id).all()
    my_total_q = sum(p.total_questions_answered for p in my_progress)
    my_correct = sum(p.correct_answers for p in my_progress)
    my_accuracy = round(my_correct / max(my_total_q, 1) * 100, 1)
    my_study_min = sum(p.total_study_time_minutes for p in my_progress)

    my_sessions = db.query(func.count(TrainingSession.id)).filter(
        TrainingSession.user_id == user.id
    ).scalar() or 0

    return {
        "success": True,
        "platform": {
            "active_users": active_users,
            "avg_competency": avg_competency,
            "total_questions_answered": total_answers,
            "total_questions_in_db": total_questions_in_db,
            "total_training_sessions": total_sessions,
            "sessions_today": sessions_today,
        },
        "personal": {
            "questions_answered": my_total_q,
            "correct_answers": my_correct,
            "accuracy": my_accuracy,
            "study_minutes": my_study_min,
            "training_sessions": my_sessions,
            "progress_by_band": [
                {
                    "band": p.current_band.value if p.current_band else None,
                    "progress_pct": p.band_progress_percentage,
                    "questions": p.total_questions_answered,
                    "correct": p.correct_answers,
                }
                for p in my_progress
            ],
        },
    }
