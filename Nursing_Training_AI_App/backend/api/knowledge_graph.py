from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List

from services.rag_service import rag_service

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])

@router.get("/data")
async def get_graph_data():
    """Get nodes and edges for the knowledge graph visualization"""
    try:
        data = await rag_service.get_knowledge_graph()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
