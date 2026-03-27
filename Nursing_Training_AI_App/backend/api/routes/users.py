"""
User profile and progress routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from models.user import User, NHSBand, UserProgress
from api.schemas.auth import UserResponse, UserProfileUpdate, MessageResponse
from api.dependencies import get_current_active_user

router = APIRouter()


# ========================================
# HEALTH CHECK
# ========================================

@router.get("/ping")
async def ping():
    return {"users": "ok"}


# ========================================
# PROFILE
# ========================================

@router.get("/me/profile", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_active_user)):
    """Returneaza profilul complet al utilizatorului autentificat"""
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        nhs_band=user.nhs_band.value if user.nhs_band else None,
        specialization=user.specialization,
        years_experience=user.years_experience,
        subscription_tier=user.subscription_tier.value if user.subscription_tier else "demo",
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.put("/me/profile", response_model=UserResponse)
async def update_profile(
    data: UserProfileUpdate,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Actualizeaza profilul utilizatorului autentificat"""

    update_data = data.model_dump(exclude_unset=True)

    # Validare NHS band daca e inclus
    if "nhs_band" in update_data and update_data["nhs_band"] is not None:
        try:
            update_data["nhs_band"] = NHSBand(update_data["nhs_band"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid NHS band. Valid values: {[b.value for b in NHSBand]}",
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        nhs_band=user.nhs_band.value if user.nhs_band else None,
        specialization=user.specialization,
        years_experience=user.years_experience,
        subscription_tier=user.subscription_tier.value if user.subscription_tier else "demo",
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login,
    )


# ========================================
# PROGRESS
# ========================================

@router.get("/me/progress")
async def get_progress(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Returneaza progresul utilizatorului pe toate band-urile"""
    progress_records = db.query(UserProgress).filter(UserProgress.user_id == user.id).all()

    progress_list = []
    for p in progress_records:
        progress_list.append({
            "id": p.id,
            "current_band": p.current_band.value if p.current_band else None,
            "band_progress_percentage": p.band_progress_percentage,
            "total_questions_answered": p.total_questions_answered,
            "correct_answers": p.correct_answers,
            "total_study_time_minutes": p.total_study_time_minutes,
            "clinical_skills_score": p.clinical_skills_score,
            "management_skills_score": p.management_skills_score,
            "communication_skills_score": p.communication_skills_score,
        })

    return {
        "success": True,
        "user_id": user.id,
        "progress": progress_list,
        "summary": {
            "total_questions": sum(p.total_questions_answered for p in progress_records),
            "total_correct": sum(p.correct_answers for p in progress_records),
            "accuracy": round(
                sum(p.correct_answers for p in progress_records)
                / max(sum(p.total_questions_answered for p in progress_records), 1)
                * 100, 1
            ),
            "total_study_minutes": sum(p.total_study_time_minutes for p in progress_records),
        },
    }


@router.delete("/me/account", response_model=MessageResponse)
async def delete_own_account(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Dezactiveaza contul utilizatorului (soft delete)"""
    user.is_active = False
    db.commit()
    return MessageResponse(success=True, message="Account deactivated successfully")
