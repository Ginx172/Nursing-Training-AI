import os
import json
import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class DemoQuestion(BaseModel):
    id: int
    title: str
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None


class SubmitAnswer(BaseModel):
    question_id: int
    user_answer: str


DEMO_QUESTIONS: List[DemoQuestion] = [
    DemoQuestion(
        id=1,
        title="Fluid rate calculation",
        question_text=(
            "A 70 kg adult requires 30 mL/kg/day maintenance fluids. Calculate the rate in mL/hour."
        ),
        question_type="calculation",
        options=None,
        correct_answer="87.5",
        explanation="70 kg x 30 mL = 2100 mL/day. 2100 / 24 h = 87.5 mL/h.",
    ),
    DemoQuestion(
        id=2,
        title="IV infusion dose",
        question_text=(
            "Administer 1 g over 30 minutes. The bag has 100 mL total volume. What is the infusion rate (mL/hour)?"
        ),
        question_type="calculation",
        options=None,
        correct_answer="200",
        explanation="100 mL over 0.5 h = 100 / 0.5 = 200 mL/h.",
    ),
    DemoQuestion(
        id=3,
        title="Escalation in sepsis",
        question_text=(
            "A patient with suspected sepsis remains hypotensive after fluids. True or False: escalate to senior support and consider antibiotics within 1 hour."
        ),
        question_type="true_false",
        options=["True", "False"],
        correct_answer="True",
        explanation="Sepsis 6 bundle recommends prompt escalation and timely antibiotics.",
    ),
]


class Recommendation(BaseModel):
    title: str
    summary: str
    url: Optional[str] = None


class SubmitResult(BaseModel):
    question_id: int
    is_correct: bool
    feedback: str
    recommendations: List[Recommendation] = []


class BatchSubmitAnswer(BaseModel):
    question_id: int
    user_answer: str


class BatchSubmitPayload(BaseModel):
    answers: List[BatchSubmitAnswer]


class PerQuestionResult(BaseModel):
    question_id: int
    is_correct: bool
    feedback: str
    recommendations: List[Recommendation] = []


def _is_correct(user_answer: str, correct_answer: str) -> bool:
    na = user_answer.strip().lower()
    nc = correct_answer.strip().lower()
    if na == nc:
        return True
    try:
        return abs(float(na) - float(nc)) < 0.01
    except Exception:
        return False


async def _gemini_evaluate(question: DemoQuestion, user_answer: str, is_correct: bool) -> Optional[dict]:
    """Apeleaza Gemini pentru feedback personalizat."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        print("GEMINI: No API key found")
        return None

    prompt = f"""You are a UK NHS nursing clinical educator. A student answered a clinical question.

QUESTION: {question.question_text}
QUESTION TYPE: {question.question_type}
CORRECT ANSWER: {question.correct_answer}
STUDENT ANSWER: {user_answer}
RESULT: {"CORRECT" if is_correct else "INCORRECT"}

Provide feedback in JSON format:
{{
  "feedback": "2-3 sentences of personalised clinical feedback explaining why the answer is correct/incorrect, with clinical reasoning",
  "recommendations": [
    {{"title": "Study topic title", "summary": "One sentence describing what to study"}},
    {{"title": "Second topic", "summary": "One sentence"}}
  ]
}}

Be encouraging but clinically precise. Reference NHS guidelines where relevant. Respond ONLY with valid JSON."""

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                gemini_url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 500}
                },
                timeout=15.0
            )
            print(f"GEMINI: status={response.status_code}, model={model}")
            if response.status_code != 200:
                print(f"GEMINI error: {response.text[:200]}")
            if response.status_code == 200:
                data = response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if content.startswith("```"):
                    content = content.split("```", 2)[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.rsplit("```", 1)[0]
                return json.loads(content.strip())
    except Exception:
        pass
    return None


def _static_feedback(question: DemoQuestion, is_correct: bool) -> dict:
    """Feedback hardcodat ca fallback."""
    if is_correct:
        fb = f"Correct! {question.explanation or ''}"
    else:
        fb = f"Incorrect. The correct answer is {question.correct_answer}. {question.explanation or ''}"

    recs = []
    if question.id == 1:
        recs = [
            {"title": "IV infusion calculations", "summary": "Refresh mL/kg/day to mL/h conversions."},
            {"title": "Common calculation errors", "summary": "Rounding, wrong units, division by 24 hours."},
        ]
    elif question.id == 2:
        recs = [
            {"title": "Time conversions", "summary": "Always convert minutes to hours for mL/h."},
            {"title": "Infusion pump setup", "summary": "Verify volume, time, and displayed units."},
        ]
    else:
        recs = [
            {"title": "Sepsis 6 bundle", "summary": "Escalation, antibiotics within 1 hour, lactate, cultures."},
            {"title": "SBAR communication", "summary": "Use SBAR for rapid and clear clinical escalation."},
        ]
    return {"feedback": fb, "recommendations": recs}


@router.get("/questions", response_model=List[DemoQuestion])
async def get_demo_questions() -> List[DemoQuestion]:
    return DEMO_QUESTIONS


@router.post("/submit", response_model=SubmitResult)
async def submit_demo_answer(payload: SubmitAnswer) -> SubmitResult:
    question = next((q for q in DEMO_QUESTIONS if q.id == payload.question_id), None)
    if question is None:
        return SubmitResult(question_id=payload.question_id, is_correct=False, feedback="Invalid question.")

    correct = _is_correct(payload.user_answer, question.correct_answer)

    # Incearca Gemini, fallback pe static
    ai_result = await _gemini_evaluate(question, payload.user_answer, correct)
    if ai_result:
        feedback = ai_result.get("feedback", "")
        recs = [Recommendation(**r) for r in ai_result.get("recommendations", [])]
    else:
        static = _static_feedback(question, correct)
        feedback = static["feedback"]
        recs = [Recommendation(**r) for r in static["recommendations"]]

    return SubmitResult(
        question_id=question.id,
        is_correct=correct,
        feedback=feedback,
        recommendations=recs,
    )


@router.post("/submit-batch")
async def submit_batch(payload: BatchSubmitPayload):
    id_to_question = {q.id: q for q in DEMO_QUESTIONS}
    per_question = []
    correct_count = 0

    for ans in payload.answers:
        q = id_to_question.get(ans.question_id)
        if not q:
            per_question.append({"question_id": ans.question_id, "is_correct": False, "feedback": "Invalid question.", "recommendations": []})
            continue

        is_ok = _is_correct(ans.user_answer, q.correct_answer)
        if is_ok:
            correct_count += 1

        ai_result = await _gemini_evaluate(q, ans.user_answer, is_ok)
        if ai_result:
            fb = ai_result.get("feedback", "")
            recs = ai_result.get("recommendations", [])
        else:
            static = _static_feedback(q, is_ok)
            fb = static["feedback"]
            recs = static["recommendations"]

        per_question.append({
            "question_id": q.id,
            "is_correct": is_ok,
            "feedback": fb,
            "recommendations": recs,
        })

    total = len(id_to_question)
    score_pct = round((correct_count / total) * 100, 1) if total else 0.0

    return {
        "total_questions": total,
        "correct": correct_count,
        "score_percentage": score_pct,
        "per_question": per_question,
        "study_plan": [
            {
                "title": "Clinical calculation fundamentals",
                "items": ["mL/kg/day to mL/h", "Minutes to hours conversions", "Pump setup verification"],
            },
            {
                "title": "Safety protocols",
                "items": ["Sepsis 6", "Escalation and SBAR communication"],
            },
        ],
        "next_steps": "Review incorrect questions, then try a new set at a higher difficulty.",
    }
