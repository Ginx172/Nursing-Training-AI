"""
Question Generator API Routes - Generate real questions from book content
Admin only. Supports pause/resume.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.rbac import Permission
from models.user import User
from api.dependencies import require_permission
from services.question_generator_service import question_generator

router = APIRouter(tags=["question-generator"])


@router.get("/status")
async def get_generator_status(
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
):
    """Status curent al generatorului de intrebari"""
    return {"success": True, **question_generator.get_status()}


@router.post("/generate")
async def generate_questions(
    count: int = Query(10, ge=1, le=100),
    specialty: Optional[str] = Query(None),
    band: Optional[str] = Query(None),
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Genereaza intrebari din continutul cartilor via RAG + Ollama"""
    result = await question_generator.generate_batch(
        db, count=count, specialty=specialty, band=band
    )
    return result


@router.post("/pause")
async def pause_generator(
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
):
    """Pause generarea de intrebari"""
    question_generator.pause()
    return {"success": True, "message": "Generator paused"}


@router.post("/resume")
async def resume_generator(
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
):
    """Resume generarea de intrebari"""
    question_generator.resume()
    return {"success": True, "message": "Generator resumed"}
