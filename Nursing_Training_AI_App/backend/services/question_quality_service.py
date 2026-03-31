"""
Question Quality Service - Deduplicare, scoring, imbunatatire cu AI
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

import httpx
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from core.config import settings
from models.training import Question

logger = logging.getLogger(__name__)

# Patterns that indicate generic/template answers
GENERIC_PATTERNS = [
    "appropriate assessment tools",
    "Monitor vital signs and observations specific to",
    "Implement evidence-based interventions for",
    "Document findings and care provided",
    "Escalate concerns appropriately in",
    "Show all working clearly",
    "Check calculation twice",
    "Demonstrate understanding of",
    "Consider team dynamics",
    "Address potential challenges proactively",
    "Show evidence-based approach",
]


class QuestionQualityService:

    def deduplicate(self, db: Session) -> Dict[str, Any]:
        """Dezactiveaza intrebarile cu question_text identic. Pastreaza prima din fiecare grup."""
        # Gaseste grupuri cu text identic
        duplicate_groups = db.query(
            Question.question_text,
            func.count(Question.id).label("cnt"),
            func.min(Question.id).label("keep_id"),
        ).filter(
            Question.is_active == True
        ).group_by(
            Question.question_text
        ).having(
            func.count(Question.id) > 1
        ).all()

        total_deactivated = 0
        groups_processed = 0

        for group in duplicate_groups:
            # Dezactiveaza toate EXCEPT cea cu ID minim
            result = db.execute(
                text("""
                    UPDATE questions
                    SET is_active = false
                    WHERE question_text = :qtext
                    AND id != :keep_id
                    AND is_active = true
                """),
                {"qtext": group.question_text, "keep_id": group.keep_id},
            )
            total_deactivated += result.rowcount
            groups_processed += 1

        db.commit()

        remaining = db.query(func.count(Question.id)).filter(
            Question.is_active == True
        ).scalar() or 0

        return {
            "duplicate_groups": groups_processed,
            "deactivated": total_deactivated,
            "remaining_active": remaining,
        }

    def get_quality_report(self, db: Session) -> Dict[str, Any]:
        """Genereaza raport de calitate pentru intrebarile active"""
        total_active = db.query(func.count(Question.id)).filter(
            Question.is_active == True
        ).scalar() or 0

        total_inactive = db.query(func.count(Question.id)).filter(
            Question.is_active == False
        ).scalar() or 0

        # Intrebari cu raspunsuri generice
        generic_count = 0
        for pattern in GENERIC_PATTERNS[:3]:  # Check top patterns
            cnt = db.query(func.count(Question.id)).filter(
                Question.is_active == True,
                Question.correct_answer.contains(pattern),
            ).scalar() or 0
            generic_count = max(generic_count, cnt)

        # Intrebari cu raspunsuri scurte (< 100 chars)
        short_answers = db.query(func.count(Question.id)).filter(
            Question.is_active == True,
            func.length(Question.correct_answer) < 100,
        ).scalar() or 0

        # Intrebari cu raspunsuri bune (> 200 chars, nu generice)
        good_answers = db.query(func.count(Question.id)).filter(
            Question.is_active == True,
            func.length(Question.correct_answer) > 200,
        ).scalar() or 0

        # Distributie per band
        by_band = db.query(
            Question.nhs_band, func.count(Question.id)
        ).filter(Question.is_active == True).group_by(Question.nhs_band).order_by(Question.nhs_band).all()

        # Distributie per specialty
        by_specialty = db.query(
            Question.specialization, func.count(Question.id)
        ).filter(Question.is_active == True).group_by(Question.specialization).order_by(
            func.count(Question.id).desc()
        ).all()

        # Sample intrebari cu raspunsuri generice
        generic_samples = db.query(Question).filter(
            Question.is_active == True,
            Question.correct_answer.contains("appropriate assessment tools"),
        ).limit(5).all()

        return {
            "total_active": total_active,
            "total_inactive": total_inactive,
            "generic_answers": generic_count,
            "generic_pct": round(generic_count / max(total_active, 1) * 100, 1),
            "short_answers": short_answers,
            "good_answers": good_answers,
            "good_pct": round(good_answers / max(total_active, 1) * 100, 1),
            "by_band": [{"band": b, "count": c} for b, c in by_band],
            "by_specialty": [{"specialty": s or "none", "count": c} for s, c in by_specialty],
            "generic_samples": [
                {
                    "id": q.id,
                    "title": q.title,
                    "band": q.nhs_band,
                    "specialty": q.specialization,
                    "answer_preview": q.correct_answer[:150] if q.correct_answer else "",
                }
                for q in generic_samples
            ],
        }

    def calculate_quality_score(self, question: Question) -> int:
        """Calculeaza scor de calitate 0-100 pentru o intrebare"""
        score = 0
        answer = question.correct_answer or ""

        # Lungime raspuns (0-30 pts)
        if len(answer) > 500:
            score += 30
        elif len(answer) > 200:
            score += 20
        elif len(answer) > 100:
            score += 10

        # Specificitate - NU contine patterns generice (0-30 pts)
        is_generic = any(p.lower() in answer.lower() for p in GENERIC_PATTERNS)
        if not is_generic:
            score += 30
        elif len(answer) > 300:
            score += 10  # Generic dar lung - partial acceptabil

        # Are explicatie (0-15 pts)
        if question.explanation and len(question.explanation) > 50:
            score += 15

        # Are optiuni (pentru multiple choice) (0-10 pts)
        if question.options and len(question.options) >= 3:
            score += 10

        # Are tags/competencies (0-10 pts)
        if question.tags and len(question.tags) >= 2:
            score += 10

        # Titlu descriptiv (0-5 pts)
        if question.title and len(question.title) > 20:
            score += 5

        return min(100, score)

    async def improve_single(self, db: Session, question_id: int) -> Dict[str, Any]:
        """Imbunatateste o singura intrebare cu Ollama"""
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return {"success": False, "error": "Question not found"}

        improved_answer = await self._call_ollama_improve(question)
        if not improved_answer:
            return {"success": False, "error": "Ollama failed to generate improved answer"}

        old_answer = question.correct_answer
        question.correct_answer = improved_answer
        db.commit()

        return {
            "success": True,
            "question_id": question_id,
            "old_answer_length": len(old_answer or ""),
            "new_answer_length": len(improved_answer),
            "new_answer_preview": improved_answer[:300],
        }

    async def improve_batch(
        self, db: Session, batch_size: int = 20, target: str = "generic"
    ) -> Dict[str, Any]:
        """Imbunatateste un batch de intrebari cu raspunsuri generice"""
        # Selecteaza intrebari cu raspunsuri generice
        query = db.query(Question).filter(Question.is_active == True)

        if target == "generic":
            query = query.filter(
                Question.correct_answer.contains("appropriate assessment tools")
            )
        elif target == "short":
            query = query.filter(func.length(Question.correct_answer) < 100)

        questions = query.limit(batch_size).all()
        if not questions:
            return {"success": True, "improved": 0, "message": "No questions to improve"}

        improved = 0
        failed = 0

        for q in questions:
            try:
                new_answer = await self._call_ollama_improve(q)
                if new_answer and len(new_answer) > len(q.correct_answer or ""):
                    q.correct_answer = new_answer
                    improved += 1
                else:
                    failed += 1
            except Exception as e:
                logger.warning(f"Failed to improve Q#{q.id}: {e}")
                failed += 1

        db.commit()

        return {
            "success": True,
            "processed": len(questions),
            "improved": improved,
            "failed": failed,
        }

    async def _call_ollama_improve(self, question: Question) -> Optional[str]:
        """Trimite intrebarea la Ollama pentru imbunatatire"""
        band_label = (question.nhs_band or "band_5").replace("_", " ").title()
        specialty_label = (question.specialization or "general").replace("_", " ").title()

        prompt = f"""You are an NHS nursing education expert creating training materials for UK healthcare professionals.

Improve this training question's answer to be specific, educational, and clinically accurate.

Question: {question.question_text}
Specialty: {specialty_label}
NHS Band: {band_label}
Difficulty: {question.difficulty_level.value if question.difficulty_level else 'intermediate'}
Current answer (generic, needs improvement): {(question.correct_answer or '')[:300]}

Write a detailed, specific correct answer (200-400 words) that includes:
- Specific clinical steps and procedures
- Relevant NHS/NICE guidelines where applicable
- Band-appropriate depth of knowledge expected
- Key safety considerations

Write ONLY the improved answer, no preamble or explanation."""

        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.4, "num_predict": 2048},
                    },
                )
                response.raise_for_status()
                answer = response.json().get("response", "").strip()
                # Filtreaza raspunsuri prea scurte sau cu tag-uri
                if len(answer) < 50:
                    return None
                # Curata potential markdown/tags
                answer = answer.replace("```", "").strip()
                return answer
        except Exception as e:
            logger.warning(f"Ollama improve failed: {e}")
            return None


# Singleton
question_quality = QuestionQualityService()
