"""
AI Brain API Routes - Ollama orchestrator endpoints
Toate endpoint-urile necesita admin authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from core.rbac import Permission
from models.user import User
from api.dependencies import require_permission
from services.ollama_brain_service import ollama_brain

router = APIRouter(tags=["ai-brain"])


@router.get("/health")
async def ai_brain_health(
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
):
    """Verifica status Ollama si disponibilitate model"""
    if not settings.OLLAMA_ENABLED:
        return {"success": True, "status": "disabled", "message": "Ollama integration is disabled in config"}

    health = await ollama_brain.health_check()
    return {"success": True, **health}


@router.post("/run-analysis")
async def run_analysis(
    days: int = Query(7, ge=1, le=90),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Trigger manual analiza platformei cu Ollama"""
    if not settings.OLLAMA_ENABLED:
        raise HTTPException(status_code=400, detail="Ollama integration is disabled")

    # Verificam ca Ollama e online
    health = await ollama_brain.health_check()
    if health.get("status") not in ("online",):
        raise HTTPException(
            status_code=503,
            detail=f"Ollama not available: {health.get('message', health.get('status'))}",
        )

    result = await ollama_brain.run_weekly_analysis(db, days=days)
    return {"success": result.get("success", False), **result}


@router.get("/insights")
async def list_insights(
    limit: int = Query(10, ge=1, le=50),
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Lista ultimelor rapoarte AI generate"""
    insights = ollama_brain.get_latest_insights(db, limit=limit)
    return {"success": True, "insights": insights, "total": len(insights)}


@router.get("/insights/{insight_id}")
async def get_insight(
    insight_id: int,
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Detalii raport AI specific"""
    insight = ollama_brain.get_insight_by_id(db, insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return {"success": True, "insight": insight}
