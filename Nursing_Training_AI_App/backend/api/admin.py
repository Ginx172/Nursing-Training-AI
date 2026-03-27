"""
Admin API Endpoints
Admin panel for managing users, content, and platform
All endpoints require admin JWT authentication.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from core.database import get_db
from models.user import User, UserRole, NHSBand, SubscriptionTier, UserProgress
from models.training import Question, QuestionType, DifficultyLevel, TrainingSession, UserAnswer
from api.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ========================================
# REQUEST / RESPONSE MODELS
# ========================================

class CreateQuestionRequest(BaseModel):
    title: str
    question_text: str
    question_type: str  # multiple_choice, true_false, calculation, scenario, case_study
    difficulty_level: str  # beginner, intermediate, advanced, expert
    nhs_band: str
    correct_answer: str
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    specialization: Optional[str] = None
    tags: Optional[List[str]] = None
    is_demo: bool = False


# ========================================
# HELPER - serializare User
# ========================================

def _serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.value if user.role else None,
        "nhs_band": user.nhs_band.value if user.nhs_band else None,
        "specialization": user.specialization,
        "years_experience": user.years_experience,
        "subscription_tier": user.subscription_tier.value if user.subscription_tier else "demo",
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


def _serialize_question(q: Question) -> dict:
    return {
        "id": q.id,
        "title": q.title,
        "question_text": q.question_text,
        "question_type": q.question_type.value if q.question_type else None,
        "difficulty_level": q.difficulty_level.value if q.difficulty_level else None,
        "nhs_band": q.nhs_band,
        "specialization": q.specialization,
        "options": q.options,
        "correct_answer": q.correct_answer,
        "explanation": q.explanation,
        "tags": q.tags,
        "is_active": q.is_active,
        "is_demo": q.is_demo,
        "created_at": q.created_at.isoformat() if q.created_at else None,
    }


# ========================================
# USER MANAGEMENT
# ========================================

@router.get("/users/search")
async def search_users(
    search_term: Optional[str] = Query(None),
    band: Optional[str] = Query(None),
    subscription_tier: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Search and filter users"""
    query = db.query(User)

    if search_term:
        term = f"%{search_term}%"
        query = query.filter(
            or_(
                User.email.ilike(term),
                User.username.ilike(term),
                User.first_name.ilike(term),
                User.last_name.ilike(term),
            )
        )

    if band:
        try:
            query = query.filter(User.nhs_band == NHSBand(band))
        except ValueError:
            pass

    if subscription_tier:
        try:
            query = query.filter(User.subscription_tier == SubscriptionTier(subscription_tier))
        except ValueError:
            pass

    if status == "active":
        query = query.filter(User.is_active == True)
    elif status == "inactive":
        query = query.filter(User.is_active == False)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "success": True,
        "users": [_serialize_user(u) for u in users],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get detailed user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Statistici din progres
    progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
    total_questions = sum(p.total_questions_answered for p in progress)
    total_correct = sum(p.correct_answers for p in progress)
    accuracy = round(total_correct / max(total_questions, 1) * 100, 1)
    total_study_min = sum(p.total_study_time_minutes for p in progress)

    # Numar sesiuni training
    session_count = db.query(func.count(TrainingSession.id)).filter(
        TrainingSession.user_id == user_id
    ).scalar() or 0

    return {
        "success": True,
        "user": {
            **_serialize_user(user),
            "activity": {
                "total_questions_answered": total_questions,
                "correct_answers": total_correct,
                "accuracy": accuracy,
                "total_study_minutes": total_study_min,
                "training_sessions": session_count,
            },
            "progress_by_band": [
                {
                    "band": p.current_band.value if p.current_band else None,
                    "progress_pct": p.band_progress_percentage,
                    "questions": p.total_questions_answered,
                    "correct": p.correct_answers,
                }
                for p in progress
            ],
        },
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    updates: Dict[str, Any] = Body(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    allowed_fields = {
        "first_name", "last_name", "nhs_band", "specialization",
        "years_experience", "subscription_tier", "is_active", "is_verified", "role",
    }
    applied = []
    for field, value in updates.items():
        if field not in allowed_fields:
            continue

        # Validare enums
        if field == "nhs_band" and value is not None:
            try:
                value = NHSBand(value)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid nhs_band: {value}")
        elif field == "subscription_tier":
            try:
                value = SubscriptionTier(value)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid subscription_tier: {value}")
        elif field == "role":
            try:
                value = UserRole(value)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid role: {value}")

        setattr(user, field, value)
        applied.append(field)

    if not applied:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "User updated successfully",
        "user_id": user_id,
        "updated_fields": applied,
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Soft-delete user account (deactivate)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")

    user.is_active = False
    db.commit()

    return {
        "success": True,
        "message": "User deactivated successfully",
        "user_id": user_id,
    }


# ========================================
# QUESTION MANAGEMENT
# ========================================

@router.get("/questions/search")
async def search_questions(
    specialty: Optional[str] = Query(None),
    band: Optional[str] = Query(None),
    question_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    search_term: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Search questions with filters"""
    query = db.query(Question)

    if specialty:
        query = query.filter(Question.specialization.ilike(f"%{specialty}%"))
    if band:
        query = query.filter(Question.nhs_band == band)
    if question_type:
        try:
            query = query.filter(Question.question_type == QuestionType(question_type))
        except ValueError:
            pass
    if difficulty:
        try:
            query = query.filter(Question.difficulty_level == DifficultyLevel(difficulty))
        except ValueError:
            pass
    if search_term:
        term = f"%{search_term}%"
        query = query.filter(
            or_(Question.title.ilike(term), Question.question_text.ilike(term))
        )

    total = query.count()
    questions = query.order_by(Question.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "success": True,
        "questions": [_serialize_question(q) for q in questions],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/questions/create", status_code=201)
async def create_question(
    data: CreateQuestionRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a new question"""
    try:
        q_type = QuestionType(data.question_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid question_type. Valid: {[t.value for t in QuestionType]}",
        )

    try:
        d_level = DifficultyLevel(data.difficulty_level)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid difficulty_level. Valid: {[d.value for d in DifficultyLevel]}",
        )

    question = Question(
        title=data.title,
        question_text=data.question_text,
        question_type=q_type,
        difficulty_level=d_level,
        nhs_band=data.nhs_band,
        correct_answer=data.correct_answer,
        options=data.options,
        explanation=data.explanation,
        specialization=data.specialization,
        tags=data.tags,
        is_demo=data.is_demo,
        is_active=True,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return {
        "success": True,
        "message": "Question created successfully",
        "question_id": question.id,
    }


@router.put("/questions/{question_id}")
async def update_question(
    question_id: int,
    updates: Dict[str, Any] = Body(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update a question"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    allowed_fields = {
        "title", "question_text", "correct_answer", "explanation",
        "options", "tags", "specialization", "nhs_band", "is_active", "is_demo",
    }

    applied = []
    for field, value in updates.items():
        if field not in allowed_fields:
            continue
        setattr(question, field, value)
        applied.append(field)

    if not applied:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    db.commit()

    return {
        "success": True,
        "message": "Question updated successfully",
        "question_id": question_id,
        "updated_fields": applied,
    }


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Soft-delete a question (deactivate)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    question.is_active = False
    db.commit()

    return {
        "success": True,
        "message": "Question deactivated successfully",
        "question_id": question_id,
    }


# ========================================
# SUBSCRIPTION MANAGEMENT
# ========================================

@router.get("/subscriptions")
async def get_all_subscriptions(
    status: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get all users with subscription info"""
    query = db.query(User)

    if tier:
        try:
            query = query.filter(User.subscription_tier == SubscriptionTier(tier))
        except ValueError:
            pass

    if status == "active":
        query = query.filter(User.is_active == True)
    elif status == "inactive":
        query = query.filter(User.is_active == False)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    subscriptions = []
    for u in users:
        subscriptions.append({
            "user_id": u.id,
            "email": u.email,
            "username": u.username,
            "subscription_tier": u.subscription_tier.value if u.subscription_tier else "demo",
            "is_active": u.is_active,
            "expires_at": u.subscription_expires_at.isoformat() if u.subscription_expires_at else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })

    return {
        "success": True,
        "subscriptions": subscriptions,
        "total": total,
    }


@router.post("/subscriptions/{user_id}/cancel")
async def admin_cancel_subscription(
    user_id: int,
    reason: str = Body(..., embed=True),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Cancel user subscription (downgrade to demo)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    previous_tier = user.subscription_tier.value if user.subscription_tier else "demo"
    user.subscription_tier = SubscriptionTier.DEMO
    user.subscription_expires_at = None
    db.commit()

    return {
        "success": True,
        "message": f"Subscription cancelled. Downgraded from {previous_tier} to demo.",
        "user_id": user_id,
        "reason": reason,
    }


# ========================================
# PLATFORM STATISTICS
# ========================================

@router.get("/stats")
async def get_platform_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get platform-wide statistics"""
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    total_questions = db.query(func.count(Question.id)).scalar() or 0
    total_answers = db.query(func.count(UserAnswer.id)).scalar() or 0
    total_sessions = db.query(func.count(TrainingSession.id)).scalar() or 0

    # Distributie pe tier-uri
    tier_counts = {}
    for tier in SubscriptionTier:
        count = db.query(func.count(User.id)).filter(
            User.subscription_tier == tier, User.is_active == True
        ).scalar() or 0
        tier_counts[tier.value] = count

    # Distributie pe roluri
    role_counts = {}
    for role in UserRole:
        count = db.query(func.count(User.id)).filter(
            User.role == role, User.is_active == True
        ).scalar() or 0
        role_counts[role.value] = count

    return {
        "success": True,
        "stats": {
            "total_users": total_users,
            "active_users": active_users,
            "total_questions_in_db": total_questions,
            "total_answers_submitted": total_answers,
            "total_training_sessions": total_sessions,
            "subscriptions_by_tier": tier_counts,
            "users_by_role": role_counts,
        },
    }


# ========================================
# SYSTEM CONFIGURATION
# ========================================

@router.get("/config")
async def get_system_config(admin: User = Depends(get_current_admin)):
    """Get system configuration"""
    from core.config import settings

    return {
        "success": True,
        "config": {
            "platform_version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "features_enabled": {
                "audio": True,
                "offline": True,
                "collaboration": True,
                "api_access": True,
            },
            "limits": {
                "max_file_size_mb": settings.MAX_FILE_SIZE // (1024 * 1024),
                "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                "refresh_token_expire_days": settings.REFRESH_TOKEN_EXPIRE_DAYS,
            },
        },
    }


@router.put("/config")
async def update_system_config(
    config_updates: Dict[str, Any] = Body(...),
    admin: User = Depends(get_current_admin),
):
    """Update system configuration (runtime only, does not persist to .env)"""
    # Nota: configuratia reala vine din env vars si nu poate fi
    # schimbata la runtime fara restart. Acest endpoint este
    # pentru feature flags viitoare stocate in DB.
    return {
        "success": True,
        "message": "Configuration endpoint ready. Feature flags will be stored in DB in a future release.",
        "received_keys": list(config_updates.keys()),
    }


# ========================================
# AUDIT LOG
# ========================================

@router.get("/audit-log")
async def get_audit_log(
    action_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    admin: User = Depends(get_current_admin),
):
    """Get audit log entries from security log files"""
    import json
    from pathlib import Path

    log_dir = Path("logs/security")
    entries = []

    if log_dir.exists():
        for log_file in sorted(log_dir.glob("security_*.jsonl"), reverse=True)[:7]:
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if action_type and entry.get("event_type") != action_type:
                                continue
                            if user_id and entry.get("source_ip") != user_id:
                                continue
                            entries.append(entry)
                        except (json.JSONDecodeError, KeyError):
                            continue
            except OSError:
                continue

    # Sortare descrescatoare dupa timestamp
    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

    return {
        "success": True,
        "logs": entries[:limit],
        "total": len(entries),
    }
