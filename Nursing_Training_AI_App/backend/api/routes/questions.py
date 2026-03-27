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

# Intrebari suplimentare care lipsesc din question banks - categorii NHS esentiale
SUPPLEMENTARY_QUESTIONS = [
    {
        "title": "Safeguarding - Vulnerable Adult",
        "question_text": "You notice bruising on an elderly patient that is inconsistent with their explanation. Describe the steps you would take to safeguard this patient.",
        "question_type": "scenario",
        "difficulty": "intermediate",
        "expected_points": ["document findings objectively", "report to safeguarding lead", "follow local safeguarding policy", "maintain patient dignity", "do not investigate yourself"],
        "competencies": ["safeguarding", "documentation", "professional duty"],
    },
    {
        "title": "Safeguarding - Child Protection",
        "question_text": "A child presents with injuries that raise concerns about non-accidental injury. What are your responsibilities and what actions would you take?",
        "question_type": "scenario",
        "difficulty": "intermediate",
        "expected_points": ["document injuries accurately", "inform designated safeguarding lead", "follow local child protection procedures", "do not confront parents", "ensure child safety", "consider MASH referral"],
        "competencies": ["safeguarding", "child protection", "documentation"],
    },
    {
        "title": "Mental Health - Risk Assessment",
        "question_text": "A patient on your ward discloses thoughts of self-harm. How would you assess and manage this situation?",
        "question_type": "scenario",
        "difficulty": "intermediate",
        "expected_points": ["immediate safety assessment", "stay with patient", "use empathetic communication", "assess suicide risk factors", "escalate to mental health liaison team", "document assessment", "implement safety plan"],
        "competencies": ["mental health", "risk assessment", "communication"],
    },
    {
        "title": "Mental Capacity Assessment",
        "question_text": "A patient is refusing a life-saving blood transfusion. Explain how you would assess their mental capacity to make this decision, referencing the Mental Capacity Act 2005.",
        "question_type": "scenario",
        "difficulty": "advanced",
        "expected_points": ["assume capacity unless proven otherwise", "two-stage test", "can they understand the information", "can they retain it", "can they weigh it up", "can they communicate their decision", "best interests if lacking capacity", "advance directives"],
        "competencies": ["mental capacity", "ethics", "legal framework"],
    },
    {
        "title": "Communication - SBAR Handover",
        "question_text": "You need to escalate a deteriorating patient to the medical team. Demonstrate how you would structure your communication using the SBAR framework.",
        "question_type": "scenario",
        "difficulty": "easy",
        "expected_points": ["Situation - identify yourself and patient", "Background - relevant history", "Assessment - current observations and concerns", "Recommendation - what you need from them"],
        "competencies": ["communication", "SBAR", "escalation"],
    },
    {
        "title": "Communication - Breaking Bad News",
        "question_text": "How would you support a patient who has just been told they have a terminal diagnosis? What communication techniques would you use?",
        "question_type": "scenario",
        "difficulty": "advanced",
        "expected_points": ["private environment", "active listening", "acknowledge emotions", "use simple language", "check understanding", "offer support resources", "involve family if patient consents", "document conversation"],
        "competencies": ["communication", "empathy", "palliative care"],
    },
    {
        "title": "Infection Prevention and Control",
        "question_text": "Describe the key principles of infection prevention and control you would apply when caring for a patient with suspected C. difficile infection.",
        "question_type": "scenario",
        "difficulty": "intermediate",
        "expected_points": ["hand hygiene with soap and water", "isolation in side room", "PPE - gloves and apron", "enhanced environmental cleaning", "antimicrobial stewardship", "stool specimen collection", "patient education"],
        "competencies": ["infection control", "patient safety"],
    },
    {
        "title": "Ethics - Consent and Confidentiality",
        "question_text": "A patient's family member asks you for information about the patient's condition, but the patient has not given consent to share. How do you handle this situation?",
        "question_type": "scenario",
        "difficulty": "intermediate",
        "expected_points": ["maintain confidentiality", "explain duty of confidentiality to family", "check if patient has given consent", "offer to help family speak with patient", "document the interaction", "exceptions - risk of harm to others"],
        "competencies": ["ethics", "confidentiality", "communication"],
    },
    {
        "title": "End of Life Care",
        "question_text": "Describe your approach to providing dignified end-of-life care for a patient and supporting their family.",
        "question_type": "scenario",
        "difficulty": "advanced",
        "expected_points": ["symptom management", "patient comfort and dignity", "anticipatory prescribing", "spiritual and cultural needs", "family support and communication", "preferred priorities of care", "DNACPR discussions", "bereavement support"],
        "competencies": ["palliative care", "empathy", "holistic care"],
    },
    {
        "title": "Patient Falls Prevention",
        "question_text": "An elderly patient on your ward has been assessed as high risk for falls. What interventions would you implement to reduce their risk?",
        "question_type": "scenario",
        "difficulty": "easy",
        "expected_points": ["falls risk assessment tool", "bed at lowest height", "call bell within reach", "non-slip footwear", "adequate lighting", "medication review", "mobility assessment", "toileting schedule", "falls care plan"],
        "competencies": ["patient safety", "risk assessment", "care planning"],
    },
    {
        "title": "Delegation and Teamwork",
        "question_text": "As a nurse in charge of a busy shift, how do you decide which tasks to delegate to healthcare assistants and what are your responsibilities when delegating?",
        "question_type": "scenario",
        "difficulty": "intermediate",
        "expected_points": ["assess competence of delegate", "match task to skill level", "clear instructions", "maintain accountability", "supervision and support", "NMC Code on delegation"],
        "competencies": ["leadership", "delegation", "teamwork"],
    },
    {
        "title": "Deteriorating Patient - NEWS2",
        "question_text": "You record a NEWS2 score of 7 for your patient. Explain the significance of this score and what actions you would take.",
        "question_type": "scenario",
        "difficulty": "intermediate",
        "expected_points": ["score of 7+ triggers urgent response", "ABCDE assessment", "increase monitoring frequency", "escalate to medical team immediately", "consider critical care outreach", "document and communicate using SBAR"],
        "competencies": ["clinical assessment", "escalation", "NEWS2"],
    },
]


def _collect_questions_from_banks(data_dir: str, prefix: str, seen_texts: set) -> list:
    """Colecteaza intrebari unice din bank-uri JSON cu un prefix dat."""
    questions = []
    try:
        files = sorted(f for f in os.listdir(data_dir) if f.lower().startswith(prefix) and f.endswith('.json'))
    except OSError:
        return questions

    for fname in files:
        try:
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                data = json.load(f)
            for q in data.get("questions", []):
                text = q.get("question_text", "").strip()
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    questions.append(q)
        except (json.JSONDecodeError, OSError):
            continue
    return questions


@router.get("/bank/{specialty}/{band}", response_model=QuestionBank)
async def get_question_bank(specialty: str, band: str):
    """Load a diverse set of questions: primary specialty + cross-specialty + NHS core topics.

    Strategy:
    - ~8 questions from selected specialty
    - ~3 questions from other specialties (cross-training)
    - ~4 supplementary questions (safeguarding, mental health, communication, ethics)
    - Drug calculations limited to max 1
    - Total: 15 unique, randomized questions
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

    seen_texts = set()

    # 1. Intrebari din specialitatea selectata
    primary_prefix = f"{specialty_clean}_{band_clean}_bank_"
    primary_qs = _collect_questions_from_banks(data_dir, primary_prefix, seen_texts)

    # Limiteaza drug calculations din primary
    drug_keywords = ['drug', 'dose', 'dosage', 'medication calculation', 'mg/kg', 'ml/h', 'infusion rate']
    non_drug = [q for q in primary_qs if not any(kw in q.get('question_text', '').lower() for kw in drug_keywords)]
    drug_qs = [q for q in primary_qs if any(kw in q.get('question_text', '').lower() for kw in drug_keywords)]

    random.shuffle(non_drug)
    random.shuffle(drug_qs)
    primary_selected = non_drug[:8] + drug_qs[:1]  # Max 1 drug calc
    random.shuffle(primary_selected)

    # 2. Intrebari cross-specialty (diversitate)
    all_specialties = ['amu', 'emergency', 'icu', 'maternity', 'mental_health', 'pediatrics', 'cardiology', 'oncology', 'neurology']
    other_specs = [s for s in all_specialties if s != specialty_clean]
    random.shuffle(other_specs)

    cross_qs = []
    for spec in other_specs[:3]:
        cross_prefix = f"{spec}_{band_clean}_bank_"
        spec_qs = _collect_questions_from_banks(data_dir, cross_prefix, seen_texts)
        # Exclude drug calculations din cross
        spec_qs = [q for q in spec_qs if not any(kw in q.get('question_text', '').lower() for kw in drug_keywords)]
        if spec_qs:
            random.shuffle(spec_qs)
            cross_qs.append(spec_qs[0])

    # 3. Intrebari suplimentare (safeguarding, mental health, communication, ethics)
    supplementary = [q.copy() for q in SUPPLEMENTARY_QUESTIONS]
    random.shuffle(supplementary)
    supp_selected = []
    for q in supplementary:
        text = q.get("question_text", "").strip()
        if text not in seen_texts:
            seen_texts.add(text)
            supp_selected.append(q)
            if len(supp_selected) >= 4:
                break

    # Combina totul
    all_selected = primary_selected[:8] + cross_qs[:3] + supp_selected[:4]

    if not all_selected:
        raise HTTPException(status_code=404, detail=f"No questions found for specialty='{specialty}' band='{band}'")

    random.shuffle(all_selected)
    final = all_selected[:MAX_QUESTIONS_PER_SESSION]

    # Re-numeroteaza
    for i, q in enumerate(final, 1):
        q["id"] = i

    return QuestionBank(
        band=band_clean,
        specialty=specialty_clean,
        version="diverse-mixed",
        questions=[Question(**q) for q in final],
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


