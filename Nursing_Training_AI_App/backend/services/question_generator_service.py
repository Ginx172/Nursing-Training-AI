"""
Question Generator Service - Genereaza intrebari REALE din continutul cartilor
Foloseste RAG Hub pentru a gasi chunks relevante si Ollama pentru a genera intrebari.
Suporta batch generation cu progress tracking si pause/resume.
"""

import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.config import settings
from models.training import Question, QuestionType, DifficultyLevel

logger = logging.getLogger(__name__)

# Progress file for pause/resume
PROGRESS_FILE = Path("data/question_gen_progress.json")

# Band to difficulty mapping
BAND_DIFFICULTY = {
    "band_2": DifficultyLevel.BEGINNER,
    "band_3": DifficultyLevel.BEGINNER,
    "band_4": DifficultyLevel.INTERMEDIATE,
    "band_5": DifficultyLevel.INTERMEDIATE,
    "band_6": DifficultyLevel.ADVANCED,
    "band_7": DifficultyLevel.ADVANCED,
    "band_8": DifficultyLevel.EXPERT,
}

SPECIALTIES = [
    "amu", "emergency", "icu", "maternity", "mental_health",
    "pediatrics", "cardiology", "neurology", "oncology",
]

NHS_BANDS = ["band_2", "band_3", "band_4", "band_5", "band_6", "band_7", "band_8"]


class QuestionGeneratorService:

    def __init__(self):
        self._running = False
        self._paused = False
        self._progress = self._load_progress()

    def _load_progress(self) -> Dict:
        if PROGRESS_FILE.exists():
            try:
                return json.loads(PROGRESS_FILE.read_text())
            except Exception:
                pass
        return {"generated": 0, "failed": 0, "last_specialty": None, "last_band": None, "status": "idle"}

    def _save_progress(self):
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROGRESS_FILE.write_text(json.dumps(self._progress, indent=2))

    def get_status(self) -> Dict:
        return {
            **self._progress,
            "running": self._running,
            "paused": self._paused,
        }

    def pause(self):
        self._paused = True
        self._progress["status"] = "paused"
        self._save_progress()

    def resume(self):
        self._paused = False

    async def generate_batch(
        self,
        db: Session,
        count: int = 10,
        specialty: Optional[str] = None,
        band: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Genereaza un batch de intrebari din continutul RAG"""
        from services.rag_hub import rag_hub

        self._running = True
        self._progress["status"] = "running"
        self._save_progress()

        generated = 0
        failed = 0
        results = []

        # Selecteaza specialty/band
        specialties = [specialty] if specialty else SPECIALTIES
        bands = [band] if band else NHS_BANDS

        for spec in specialties:
            for b in bands:
                if generated >= count:
                    break
                if self._paused:
                    self._progress["status"] = "paused"
                    self._save_progress()
                    self._running = False
                    return {"success": True, "generated": generated, "failed": failed,
                            "paused": True, "results": results}

                # Cauta chunks relevante din RAG
                search_query = f"{spec} nursing clinical assessment {b.replace('_', ' ')}"
                chunks = rag_hub.search(search_query, k=3, source_filter="pdf")

                if not chunks:
                    # Fallback: cauta fara specialty
                    chunks = rag_hub.search(f"nursing clinical {b.replace('_', ' ')}", k=3)

                if not chunks:
                    failed += 1
                    continue

                # Trimite la Ollama cu context din chunk
                context_text = chunks[0].get("content", "")[:1500]
                source_name = chunks[0].get("source", "Unknown")

                question_data = await self._generate_from_context(
                    context_text, spec, b, source_name
                )

                if question_data:
                    # Salveaza in DB
                    saved = self._save_question(db, question_data, spec, b, source_name)
                    if saved:
                        generated += 1
                        results.append({
                            "title": question_data.get("title", ""),
                            "specialty": spec,
                            "band": b,
                            "source": source_name,
                        })
                        self._progress["generated"] = self._progress.get("generated", 0) + 1
                        self._progress["last_specialty"] = spec
                        self._progress["last_band"] = b
                    else:
                        failed += 1
                else:
                    failed += 1

        self._progress["status"] = "completed"
        self._progress["failed"] = self._progress.get("failed", 0) + failed
        self._save_progress()
        self._running = False

        return {
            "success": True,
            "generated": generated,
            "failed": failed,
            "results": results,
        }

    async def _generate_from_context(
        self, context: str, specialty: str, band: str, source: str
    ) -> Optional[Dict]:
        """Genereaza o intrebare din context cu Ollama"""
        band_label = band.replace("_", " ").title()
        spec_label = specialty.replace("_", " ").title()

        prompt = f"""You are an NHS nursing exam question writer. Based ONLY on the following textbook excerpt, create ONE exam question.

TEXTBOOK EXCERPT:
{context}

Requirements:
- Specialty: {spec_label}
- NHS Band level: {band_label}
- The question must be answerable from the text above
- The answer must use specific information from the text
- Include the source reference

Respond ONLY with valid JSON (no markdown):
{{
  "title": "Short descriptive title (max 80 chars)",
  "question_text": "The full question (1-3 sentences)",
  "question_type": "scenario",
  "correct_answer": "Detailed correct answer (150-300 words) based on the textbook text",
  "explanation": "Why this is correct, referencing the source material",
  "competencies": ["list", "of", "competencies", "tested"]
}}"""

        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.5, "num_predict": 2048},
                    },
                )
                response.raise_for_status()
                raw = response.json().get("response", "")

            # Parse JSON
            return self._parse_question_json(raw)
        except Exception as e:
            logger.warning(f"Ollama question generation failed: {e}")
            return None

    def _parse_question_json(self, raw: str) -> Optional[Dict]:
        """Parseaza raspunsul JSON de la Ollama"""
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        # Cauta JSON intre { si }
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                pass
        return None

    def _save_question(
        self, db: Session, data: Dict, specialty: str, band: str, source: str
    ) -> bool:
        """Salveaza intrebarea generata in DB"""
        try:
            title = data.get("title", "Generated Question")[:500]
            q_text = data.get("question_text", "")
            answer = data.get("correct_answer", "")
            explanation = data.get("explanation", "")
            competencies = data.get("competencies", [])

            if not q_text or not answer or len(answer) < 50:
                return False

            q_type_str = data.get("question_type", "scenario")
            try:
                q_type = QuestionType(q_type_str)
            except ValueError:
                q_type = QuestionType.SCENARIO

            difficulty = BAND_DIFFICULTY.get(band, DifficultyLevel.INTERMEDIATE)

            question = Question(
                title=title,
                question_text=q_text[:5000],
                question_type=q_type,
                difficulty_level=difficulty,
                nhs_band=band,
                specialization=specialty,
                correct_answer=answer[:5000],
                explanation=f"{explanation}\n\nSource: {source}"[:5000] if explanation else f"Source: {source}",
                tags=competencies[:10] if competencies else None,
                is_active=True,
                is_demo=False,
            )
            db.add(question)
            db.commit()
            return True
        except Exception as e:
            logger.warning(f"Failed to save question: {e}")
            db.rollback()
            return False


# Singleton
question_generator = QuestionGeneratorService()
