from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from core.ai_evaluation import ai_evaluation_service, EvaluationResult


router = APIRouter()


class Question(BaseModel):
    id: int
    title: str
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    difficulty: Optional[str] = None
    competencies: Optional[List[str]] = None
    expected_points: Optional[List[str]] = None


class QuestionBank(BaseModel):
    band: str
    specialty: str
    version: str
    questions: List[Question]


class EvaluationRequest(BaseModel):
    question: Dict[str, Any]
    user_answer: str
    band: str
    specialty: str


class EvaluationResponse(BaseModel):
    question_id: int
    band: str
    specialty: str
    overall_score: float
    detailed_scores: Dict[str, float]
    feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    knowledge_gaps: List[str]
    book_recommendations: List[Dict[str, str]]
    next_steps: List[str]


def _load_bank(relative_path: str) -> QuestionBank:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_path = os.path.join(base_dir, 'data', 'question_banks', relative_path)
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail=f"Question bank not found: {relative_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return QuestionBank(**data)


@router.get("/amu/band5", response_model=QuestionBank)
async def get_amu_band5():
    return _load_bank('band5_amu.json')


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_answer(request: EvaluationRequest):
    """Evaluează un răspuns folosind AI, MCP și RAG pentru orice band și specialitate"""
    try:
        result = await ai_evaluation_service.evaluate_answer(
            question=request.question,
            user_answer=request.user_answer,
            band=request.band,
            specialty=request.specialty
        )
        
        return EvaluationResponse(
            question_id=result.question_id,
            band=result.band,
            specialty=result.specialty,
            overall_score=result.overall_score,
            detailed_scores=result.detailed_scores,
            feedback=result.feedback,
            strengths=result.strengths,
            areas_for_improvement=result.areas_for_improvement,
            knowledge_gaps=result.knowledge_gaps,
            book_recommendations=result.book_recommendations,
            next_steps=result.next_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/bands", response_model=List[Dict[str, str]])
async def get_available_bands():
    """Returnează toate banzile disponibile"""
    return [
        {"id": "band_2", "name": "Band 2", "description": "Healthcare Assistant"},
        {"id": "band_3", "name": "Band 3", "description": "Senior Healthcare Assistant"},
        {"id": "band_4", "name": "Band 4", "description": "Assistant Practitioner"},
        {"id": "band_5", "name": "Band 5", "description": "Staff Nurse"},
        {"id": "band_6", "name": "Band 6", "description": "Senior Staff Nurse"},
        {"id": "band_7", "name": "Band 7", "description": "Clinical Nurse Specialist"},
        {"id": "band_8a", "name": "Band 8A", "description": "Advanced Nurse Practitioner"},
        {"id": "band_8b", "name": "Band 8B", "description": "Senior Advanced Nurse Practitioner"},
        {"id": "band_8c", "name": "Band 8C", "description": "Consultant Nurse"},
        {"id": "band_8d", "name": "Band 8D", "description": "Senior Consultant Nurse"},
        {"id": "band_9", "name": "Band 9", "description": "Director of Nursing"}
    ]


@router.get("/specialties", response_model=List[Dict[str, str]])
async def get_available_specialties():
    """Returnează toate specialitățile disponibile"""
    return [
        {"id": "amu", "name": "Acute Medical Unit", "description": "Acute medical care and assessment"},
        {"id": "icu", "name": "Intensive Care Unit", "description": "Critical care and intensive monitoring"},
        {"id": "emergency", "name": "Emergency Department", "description": "Emergency and trauma care"},
        {"id": "maternity", "name": "Maternity", "description": "Maternal and newborn care"},
        {"id": "mental_health", "name": "Mental Health", "description": "Mental health and psychiatric care"},
        {"id": "pediatrics", "name": "Pediatrics", "description": "Child and adolescent healthcare"},
        {"id": "oncology", "name": "Oncology", "description": "Cancer care and treatment"},
        {"id": "cardiology", "name": "Cardiology", "description": "Heart and cardiovascular care"},
        {"id": "neurology", "name": "Neurology", "description": "Brain and nervous system care"}
    ]


