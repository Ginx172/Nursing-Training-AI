from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import random
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

    # Deduplicare: elimina intrebarile cu acelasi question_text
    seen_texts = set()
    unique_questions = []
    for q in data.get("questions", []):
        text = q.get("question_text", "").strip()
        if text and text not in seen_texts:
            seen_texts.add(text)
            unique_questions.append(q)
    data["questions"] = unique_questions

    return QuestionBank(**data)


@router.get("/amu/band5", response_model=QuestionBank)
async def get_amu_band5():
    return _load_bank('amu_band_5_bank_01.json')


MAX_QUESTIONS_PER_SESSION = 15


@router.get("/bank/{specialty}/{band}", response_model=QuestionBank)
async def get_question_bank(specialty: str, band: str):
    """Load questions from ALL available banks for a specialty/band combo,
    deduplicate, randomize, and return a set of up to MAX_QUESTIONS_PER_SESSION.

    Accepts band values like 'band_5', 'band5', or '5' (all normalised internally).
    """
    band_clean = band.strip().lower().replace(" ", "_")
    if not band_clean.startswith("band_"):
        if band_clean.startswith("band"):
            band_clean = "band_" + band_clean[4:]
        else:
            band_clean = "band_" + band_clean

    specialty_clean = specialty.strip().lower()

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'question_banks')

    prefix = f"{specialty_clean}_{band_clean}_bank_"
    try:
        files = sorted(
            f for f in os.listdir(data_dir)
            if f.lower().startswith(prefix) and f.endswith('.json')
        )
    except OSError:
        raise HTTPException(status_code=404, detail="Question bank directory not found")

    if not files:
        raise HTTPException(
            status_code=404,
            detail=f"No question bank found for specialty='{specialty}' band='{band}'"
        )

    # Colecteaza intrebari din TOATE bank-urile disponibile
    all_questions = []
    seen_texts = set()
    for fname in files:
        fpath = os.path.join(data_dir, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for q in data.get("questions", []):
                text = q.get("question_text", "").strip()
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    all_questions.append(q)
        except (json.JSONDecodeError, OSError):
            continue

    if not all_questions:
        raise HTTPException(status_code=404, detail="No valid questions found")

    # Randomizeaza si limiteaza
    random.shuffle(all_questions)
    selected = all_questions[:MAX_QUESTIONS_PER_SESSION]

    # Re-numeroteaza ID-urile secvential (1, 2, 3...)
    for i, q in enumerate(selected, 1):
        q["id"] = i

    return QuestionBank(
        band=band_clean,
        specialty=specialty_clean,
        version="multi-bank-randomized",
        questions=[Question(**q) for q in selected],
    )


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


class SubmitAnswerItem(BaseModel):
    question_id: int
    question_text: str = ""
    question_title: str = ""
    user_answer: str
    correct_answer: str = ""
    expected_points: Optional[List[str]] = None


class SubmitBatchRequest(BaseModel):
    answers: List[SubmitAnswerItem]
    band: str = ""
    specialty: str = ""


@router.post("/submit-interview")
async def submit_interview(payload: SubmitBatchRequest):
    """Submit all interview answers and get detailed feedback per question.

    For each question, provides:
    - Whether the answer was adequate
    - What was good in the answer
    - What was missing or incorrect
    - The ideal/model answer
    - Score out of 10
    """
    per_question = []
    total_score = 0

    for ans in payload.answers:
        user_ans = ans.user_answer.strip()
        correct = ans.correct_answer.strip() if ans.correct_answer else ""
        expected = ans.expected_points or []
        q_text = ans.question_text or f"Question {ans.question_id}"
        q_title = ans.question_title or ""

        # Evaluare: pentru intrebari cu raspuns exact (multiple choice / calcul)
        if correct:
            is_match = user_ans.lower() == correct.lower()
            # Verificare numerica
            try:
                is_match = is_match or abs(float(user_ans) - float(correct)) < 0.01
            except (ValueError, TypeError):
                pass

            if is_match:
                score = 10
                feedback = "Excellent! Your answer is correct."
                strengths = ["Correct answer provided"]
                weaknesses = []
                ideal = correct
            else:
                score = 2
                feedback = "Incorrect answer."
                strengths = ["You attempted the question"] if user_ans else []
                weaknesses = ["The answer does not match the expected response"]
                ideal = correct

        # Evaluare: pentru intrebari deschise (scenario-based)
        elif expected and user_ans:
            matched_points = []
            missed_points = []
            for point in expected:
                if point.lower() in user_ans.lower():
                    matched_points.append(point)
                else:
                    missed_points.append(point)

            coverage = len(matched_points) / max(len(expected), 1)
            score = round(min(coverage * 10, 10), 1)
            strengths = [f"Mentioned: {p}" for p in matched_points] if matched_points else []
            weaknesses = [f"Missing: {p}" for p in missed_points] if missed_points else []

            if coverage >= 0.8:
                feedback = "Very good! You covered most of the key points."
            elif coverage >= 0.5:
                feedback = "Adequate answer, but some important points are missing."
            elif coverage > 0:
                feedback = "Partial answer. Several key clinical points were not addressed."
            else:
                feedback = "Your answer did not address the expected clinical points."

            ideal = "Key points expected: " + "; ".join(expected)

        # Evaluare: intrebare deschisa fara expected_points
        elif user_ans:
            score = 5
            word_count = len(user_ans.split())
            if word_count >= 50:
                score = 7
                feedback = "You provided a detailed response. Review the model answer to identify areas for improvement."
                strengths = ["Detailed and comprehensive response"]
            elif word_count >= 20:
                score = 5
                feedback = "Reasonable answer but could be more detailed. Consider clinical reasoning and evidence-based practice."
                strengths = ["Addressed the question"]
            else:
                score = 3
                feedback = "Brief answer. In a clinical interview, more detail and clinical reasoning is expected."
                strengths = ["Attempted the question"]

            weaknesses = ["Consider adding more clinical detail and evidence-based reasoning"]
            ideal = "A strong answer would include: clinical assessment approach, relevant observations, differential diagnoses, escalation criteria, and evidence-based interventions."

        # Nu a raspuns
        else:
            score = 0
            feedback = "No answer provided."
            strengths = []
            weaknesses = ["Question was not answered"]
            ideal = "Please attempt all questions, even with a brief response."

        total_score += score
        per_question.append({
            "question_id": ans.question_id,
            "question_title": q_title,
            "question_text": q_text[:200],
            "user_answer": user_ans[:500] if user_ans else "(no answer)",
            "score": score,
            "max_score": 10,
            "feedback": feedback,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "ideal_answer": ideal,
            "is_correct": score >= 8,
        })

    total_possible = len(payload.answers) * 10
    score_pct = round((total_score / max(total_possible, 1)) * 100, 1)

    # Sumar general
    correct_count = sum(1 for q in per_question if q["is_correct"])
    weak_areas = []
    for q in per_question:
        if not q["is_correct"]:
            weak_areas.extend(q["weaknesses"])

    return {
        "total_questions": len(payload.answers),
        "correct": correct_count,
        "score_percentage": score_pct,
        "total_score": total_score,
        "total_possible": total_possible,
        "per_question": per_question,
        "study_plan": [
            {
                "title": "Review your weak areas",
                "items": list(set(weak_areas))[:5] if weak_areas else ["Great job! Keep practising."],
            },
        ],
        "next_steps": f"You scored {score_pct}%. "
            + ("Excellent performance! " if score_pct >= 80 else "")
            + ("Good effort, focus on the areas flagged above. " if 50 <= score_pct < 80 else "")
            + ("Review the model answers carefully and try again. " if score_pct < 50 else "")
            + "Review incorrect questions, then try a new set at a higher difficulty.",
    }


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


