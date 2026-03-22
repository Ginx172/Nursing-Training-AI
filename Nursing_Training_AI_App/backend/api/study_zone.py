from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from services.rag_service import rag_service

router = APIRouter(prefix="/study", tags=["Study Zone"])

class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    question_count: int = 5

class QuizResponse(BaseModel):
    topic: str
    questions: List[Dict[str, Any]]

@router.get("/topics", response_model=List[str])
async def get_topics():
    """Get all available study topics from the knowledge base"""
    try:
        topics = await rag_service.get_topics()
        return topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """Generate a quiz for a specific topic"""
    try:
        quiz = await rag_service.generate_quiz(request.topic, request.difficulty)
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_recommendations(
    topic: str, 
    specialty: str = "General", 
    band: str = "Band 5"
):
    """Get study recommendations based on a topic"""
    try:
        recs = await rag_service.get_recommendations(topic, specialty, band)
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
