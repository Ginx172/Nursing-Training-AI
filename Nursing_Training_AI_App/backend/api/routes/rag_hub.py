"""
RAG Hub API Routes - Unified search across FAISS + ChromaDB
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.rbac import Permission
from models.user import User
from api.dependencies import get_current_active_user, require_permission

router = APIRouter(tags=["rag-hub"])


@router.get("/search")
async def unified_search(
    q: str = Query(..., min_length=2, max_length=500),
    k: int = Query(5, ge=1, le=20),
    source: Optional[str] = Query(None, description="Filter: pdf, questions, or None for all"),
    specialty: Optional[str] = Query(None),
    user: User = Depends(get_current_active_user),
):
    """Cautare unificata in Knowledge Base (PDFs) + Question Bank (DB)"""
    from services.rag_hub import rag_hub
    results = rag_hub.search(q, k=k, source_filter=source, specialty=specialty)
    return {
        "success": True,
        "query": q,
        "results": results,
        "total": len(results),
    }


@router.get("/stats")
async def rag_stats(
    user: User = Depends(get_current_active_user),
):
    """Statistici despre indexurile RAG disponibile"""
    from services.rag_hub import rag_hub
    return {"success": True, **rag_hub.get_stats()}


@router.post("/reindex-questions")
async def reindex_questions(
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Reindexeaza toate intrebarile din PostgreSQL in ChromaDB (admin only)"""
    from services.rag_hub import rag_hub
    result = rag_hub.index_db_questions(db)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Indexing failed"))
    return {"success": True, **result}


@router.get("/context")
async def get_context(
    q: str = Query(..., min_length=2, max_length=500),
    specialty: Optional[str] = Query(None),
    band: Optional[str] = Query(None),
    user: User = Depends(get_current_active_user),
):
    """Construieste context din RAG pentru AI evaluation"""
    from services.rag_hub import rag_hub
    context = rag_hub.build_context(q, specialty=specialty, band=band)
    return {"success": True, "context": context}
