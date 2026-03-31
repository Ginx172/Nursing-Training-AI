"""
Question Quality API Routes - Deduplicare, quality report, AI improvement
Admin only endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.rbac import Permission
from models.user import User
from api.dependencies import require_permission
from services.question_quality_service import question_quality

router = APIRouter(tags=["question-quality"])


@router.get("/quality-report")
async def get_quality_report(
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Raport de calitate pentru intrebarile din DB"""
    report = question_quality.get_quality_report(db)
    return {"success": True, **report}


@router.post("/deduplicate")
async def run_deduplication(
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Dezactiveaza intrebarile duplicate (pastreaza 1 din fiecare grup)"""
    result = question_quality.deduplicate(db)
    return {"success": True, **result}


@router.post("/improve-batch")
async def improve_batch(
    batch_size: int = Query(20, ge=1, le=100),
    target: str = Query("generic", description="generic or short"),
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Imbunatateste un batch de intrebari cu Ollama AI"""
    result = await question_quality.improve_batch(db, batch_size=batch_size, target=target)
    return {"success": True, **result}


@router.post("/improve/{question_id}")
async def improve_single(
    question_id: int,
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Imbunatateste o singura intrebare cu Ollama AI"""
    result = await question_quality.improve_single(db, question_id)
    return result
