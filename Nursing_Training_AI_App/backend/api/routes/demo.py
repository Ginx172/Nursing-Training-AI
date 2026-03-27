from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict


router = APIRouter()


class DemoQuestion(BaseModel):
    id: int
    title: str
    question_text: str
    question_type: str  # multiple_choice | true_false | calculation | scenario
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
        explanation=(
            "70 kg × 30 mL = 2100 mL/day. 2100 / 24 h = 87.5 mL/h."
        ),
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
        explanation=(
            "100 mL over 0.5 h → 100 / 0.5 = 200 mL/h."
        ),
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
        explanation=(
            "Sepsis 6 bundle recommends prompt escalation and timely antibiotics."
        ),
    ),
]


@router.get("/questions", response_model=List[DemoQuestion])
async def get_demo_questions() -> List[DemoQuestion]:
    return DEMO_QUESTIONS


class Recommendation(BaseModel):
    title: str
    summary: str
    url: Optional[str] = None  # text-only; link optional


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


@router.post("/submit", response_model=SubmitResult)
async def submit_demo_answer(payload: SubmitAnswer) -> SubmitResult:
    question = next((q for q in DEMO_QUESTIONS if q.id == payload.question_id), None)
    if question is None:
        return SubmitResult(
            question_id=payload.question_id,
            is_correct=False,
            feedback="Invalid question.",
        )

    normalized_correct = question.correct_answer.strip().lower()
    normalized_user = payload.user_answer.strip().lower()

    # Allow small tolerance for numeric answers
    def is_numeric_equal(a: str, b: str) -> bool:
        try:
            return abs(float(a) - float(b)) < 0.01
        except Exception:
            return False

    correct = (
        normalized_user == normalized_correct
        or is_numeric_equal(normalized_user, normalized_correct)
    )

    # Build AI-like textual feedback with steps
    if question.id == 1:
        steps = (
            "1) Daily requirement = weight x 30 mL/kg\n"
            "2) 70 x 30 = 2100 mL/day\n"
            "3) Hourly rate = 2100 / 24 = 87.5 mL/h"
        )
        topic_recs = [
            Recommendation(
                title="IV infusion calculations: mL/hour and mL/kg/day",
                summary="Refresh basic formulas and daily-to-hourly conversions.",
                url=None,
            ),
            Recommendation(
                title="Common clinical calculation errors",
                summary="Rounding, wrong units, division by 24 hours.",
                url=None,
            ),
        ]
        if correct:
            feedback = (
                "Correct! You applied the maintenance formula correctly.\n" + steps
            )
        else:
            feedback = (
                "Incorrect."
                f"Correct answer: {question.correct_answer}.\n"
                + (question.explanation or "")
                + "\n" + steps
            )
        recs = topic_recs

    elif question.id == 2:
        steps = (
            "1) Total volume = 100 mL\n"
            "2) Time = 30 minutes = 0.5 hours\n"
            "3) Rate = volume / time = 100 / 0.5 = 200 mL/h"
        )
        topic_recs = [
            Recommendation(
                title="Time conversions: minutes to hours",
                summary="Always convert minutes to hours for mL/h.",
                url=None,
            ),
            Recommendation(
                title="Infusion pump setup",
                summary="Always verify volume, time, and displayed units.",
                url=None,
            ),
        ]
        if correct:
            feedback = "Correct! The rate calculation is accurate.\n" + steps
        else:
            feedback = (
                "Incorrect."
                f"Correct answer: {question.correct_answer}.\n"
                + (question.explanation or "")
                + "\n" + steps
            )
        recs = topic_recs

    else:  # question.id == 3
        rationale = (
            "Rapid escalation and early antibiotics are part of the Sepsis 6 bundle. "
            "Maintaining blood pressure and reviewing fluid response are critical."
        )
        topic_recs = [
            Recommendation(
                title="Sepsis 6 - key elements",
                summary="Escalation, antibiotics within 1 hour, lactate, cultures, fluids, urine output.",
                url=None,
            ),
            Recommendation(
                title="Escalation and SBAR communication",
                summary="Use the SBAR framework for rapid and clear communication.",
                url=None,
            ),
        ]
        if correct:
            feedback = "Correct!" + rationale
        else:
            feedback = (
                "Incorrect.Correct answer: True. " + rationale
            )
        recs = topic_recs

    return SubmitResult(
        question_id=question.id,
        is_correct=correct,
        feedback=feedback,
        recommendations=recs,
    )


@router.post("/submit-batch")
async def submit_batch(payload: BatchSubmitPayload):
    """Receives all answers, returns feedback only at the end (aggregated)."""

    id_to_question = {q.id: q for q in DEMO_QUESTIONS}
    per_question: List[PerQuestionResult] = []
    correct_count = 0

    for ans in payload.answers:
        q = id_to_question.get(ans.question_id)
        if not q:
            per_question.append(
                PerQuestionResult(
                    question_id=ans.question_id,
                    is_correct=False,
                    feedback="Invalid question.",
                    recommendations=[],
                )
            )
            continue

        normalized_correct = q.correct_answer.strip().lower()
        normalized_user = ans.user_answer.strip().lower()

        def is_numeric_equal(a: str, b: str) -> bool:
            try:
                return abs(float(a) - float(b)) < 0.01
            except Exception:
                return False

        is_ok = normalized_user == normalized_correct or is_numeric_equal(normalized_user, normalized_correct)
        if is_ok:
            correct_count += 1

        # Build condensed feedback per question (without revealing answers if desired)
        fb = "Correct answer" if is_ok else "Incorrect answer"

        # Minimal recommendations per question topic
        recs: List[Recommendation] = []
        if q.id == 1:
            recs = [Recommendation(title="Basic infusion calculations", summary="mL/kg/day and conversion to mL/h.")]
        elif q.id == 2:
            recs = [Recommendation(title="Time to rate conversions", summary="Minutes to hours, total volumes.")]
        elif q.id == 3:
            recs = [Recommendation(title="Sepsis 6 and escalation", summary="Key steps and SBAR.")]

        per_question.append(
            PerQuestionResult(
                question_id=q.id,
                is_correct=is_ok,
                feedback=fb,
                recommendations=recs,
            )
        )

    total = len(id_to_question)
    score_pct = round((correct_count / total) * 100, 1) if total else 0.0

    # Final structured feedback summary
    final_summary = {
        "total_questions": total,
        "correct": correct_count,
        "score_percentage": score_pct,
        "per_question": [r.model_dump() for r in per_question],
        "study_plan": [
            {
                "title": "Consolidate clinical calculation fundamentals",
                "items": [
                    "mL/kg/day to mL/h",
                    "Minutes to hours conversions",
                    "Pump setup and unit verification",
                ],
            },
            {
                "title": "Safety and protocols",
                "items": [
                    "Sepsis 6",
                    "Escalation and SBAR communication",
                ],
            },
        ],
        "next_steps": "Review incorrect questions, then try a new set at a higher difficulty.",
    }

    return final_summary


