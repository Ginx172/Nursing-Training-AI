"""
Ollama Brain Service - Central AI Orchestrator
Analizeaza periodic datele platformei si genereaza insights + recomandari.
Foloseste Ollama local cu qwen3:8b.
"""

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any

import httpx
from sqlalchemy import func, case, cast, Date
from sqlalchemy.orm import Session

from core.config import settings
from models.user import User, UserRole, SubscriptionTier, UserProgress
from models.training import Question, UserAnswer, TrainingSession, QuestionType, DifficultyLevel
from models.ai_insights import AIInsight


class OllamaBrainService:
    """Serviciu central de analiza AI bazat pe Ollama local"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    async def health_check(self) -> Dict[str, Any]:
        """Verifica daca Ollama e pornit si modelul e disponibil"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code != 200:
                    return {"status": "error", "message": f"Ollama returned {resp.status_code}"}

                models = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                model_available = any(self.model in name for name in model_names)

                return {
                    "status": "online" if model_available else "model_missing",
                    "ollama_url": self.base_url,
                    "target_model": self.model,
                    "available_models": model_names,
                    "model_ready": model_available,
                }
        except httpx.ConnectError:
            return {"status": "offline", "message": "Cannot connect to Ollama. Run: ollama serve"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def run_weekly_analysis(self, db: Session, days: int = 7) -> Dict[str, Any]:
        """Ruleaza analiza completa a platformei"""
        now = datetime.now(timezone.utc)
        period_start = now - timedelta(days=days)

        # Creeaza record in DB
        insight = AIInsight(
            report_type="weekly_analysis",
            status="running",
            model_used=self.model,
            analysis_period_start=period_start,
            analysis_period_end=now,
        )
        db.add(insight)
        db.commit()
        db.refresh(insight)

        start_time = time.time()

        try:
            # Colecteaza date
            platform_data = self._gather_platform_data(db, period_start, now)

            # Construieste prompt
            prompt = self._build_analysis_prompt(platform_data, days)

            # Apeleaza Ollama
            raw_response = await self._call_ollama(prompt)

            # Parseaza raspunsul
            parsed = self._parse_response(raw_response)

            # Actualizeaza record
            elapsed = round(time.time() - start_time, 1)
            insight.status = "completed"
            insight.insights = parsed.get("insights", [])
            insight.recommendations = parsed.get("recommendations", [])
            insight.raw_response = raw_response
            insight.generation_time_seconds = elapsed
            db.commit()

            return {
                "success": True,
                "insight_id": insight.id,
                "generation_time_seconds": elapsed,
                "insights_count": len(parsed.get("insights", [])),
                "recommendations_count": len(parsed.get("recommendations", [])),
            }

        except Exception as e:
            elapsed = round(time.time() - start_time, 1)
            insight.status = "failed"
            insight.error_message = str(e)
            insight.generation_time_seconds = elapsed
            db.commit()

            return {"success": False, "insight_id": insight.id, "error": str(e)}

    def _gather_platform_data(
        self, db: Session, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Extrage date agregate din DB pentru analiza"""
        data: Dict[str, Any] = {}

        # --- Users ---
        data["total_users"] = db.query(func.count(User.id)).scalar() or 0
        data["active_users"] = db.query(func.count(User.id)).filter(
            User.is_active == True
        ).scalar() or 0
        data["new_users"] = db.query(func.count(User.id)).filter(
            User.created_at >= period_start
        ).scalar() or 0

        # Users by role
        role_counts = db.query(
            User.role, func.count(User.id)
        ).filter(User.is_active == True).group_by(User.role).all()
        data["users_by_role"] = {
            (r.value if r else "unknown"): c for r, c in role_counts
        }

        # Users by tier
        tier_counts = db.query(
            User.subscription_tier, func.count(User.id)
        ).filter(User.is_active == True).group_by(User.subscription_tier).all()
        data["users_by_tier"] = {
            (t.value if t else "demo"): c for t, c in tier_counts
        }

        # --- Answers in period ---
        total_answers = db.query(func.count(UserAnswer.id)).filter(
            UserAnswer.answered_at >= period_start
        ).scalar() or 0
        correct_answers = db.query(func.count(UserAnswer.id)).filter(
            UserAnswer.answered_at >= period_start, UserAnswer.is_correct == True
        ).scalar() or 0
        data["questions_answered"] = total_answers
        data["correct_answers"] = correct_answers
        data["avg_accuracy_pct"] = round(
            correct_answers / max(total_answers, 1) * 100, 1
        )

        # Active learners (users who answered questions in period)
        data["active_learners"] = db.query(
            func.count(func.distinct(UserAnswer.user_id))
        ).filter(UserAnswer.answered_at >= period_start).scalar() or 0

        # --- Training sessions ---
        data["training_sessions"] = db.query(func.count(TrainingSession.id)).filter(
            TrainingSession.started_at >= period_start
        ).scalar() or 0
        data["completed_sessions"] = db.query(func.count(TrainingSession.id)).filter(
            TrainingSession.started_at >= period_start,
            TrainingSession.is_completed == True,
        ).scalar() or 0
        avg_score = db.query(func.avg(TrainingSession.score_percentage)).filter(
            TrainingSession.started_at >= period_start,
            TrainingSession.is_completed == True,
        ).scalar()
        data["avg_session_score"] = round(float(avg_score or 0), 1)

        # --- Hardest questions (< 40% accuracy, min 5 attempts) ---
        hard_q = db.query(
            Question.id,
            Question.title,
            Question.nhs_band,
            Question.specialization,
            func.count(UserAnswer.id).label("attempts"),
            func.sum(case((UserAnswer.is_correct == True, 1), else_=0)).label("correct"),
        ).join(Question, UserAnswer.question_id == Question.id).filter(
            UserAnswer.answered_at >= period_start
        ).group_by(
            Question.id, Question.title, Question.nhs_band, Question.specialization
        ).having(
            func.count(UserAnswer.id) >= 5
        ).all()

        data["hardest_questions"] = sorted(
            [
                {
                    "id": q.id, "title": q.title[:80], "band": q.nhs_band,
                    "specialty": q.specialization,
                    "attempts": q.attempts, "accuracy": round(int(q.correct or 0) / q.attempts * 100, 1),
                }
                for q in hard_q
                if int(q.correct or 0) / max(q.attempts, 1) < 0.4
            ],
            key=lambda x: x["accuracy"],
        )[:10]

        data["easiest_questions"] = sorted(
            [
                {
                    "id": q.id, "title": q.title[:80], "band": q.nhs_band,
                    "accuracy": round(int(q.correct or 0) / q.attempts * 100, 1),
                }
                for q in hard_q
                if int(q.correct or 0) / max(q.attempts, 1) > 0.95
            ],
            key=lambda x: -x["accuracy"],
        )[:10]

        # --- Performance by specialty ---
        spec_stats = db.query(
            Question.specialization,
            func.count(UserAnswer.id).label("total"),
            func.sum(case((UserAnswer.is_correct == True, 1), else_=0)).label("correct"),
        ).join(Question, UserAnswer.question_id == Question.id).filter(
            UserAnswer.answered_at >= period_start,
            Question.specialization.isnot(None),
        ).group_by(Question.specialization).all()

        data["specialty_performance"] = [
            {
                "specialty": row.specialization,
                "answers": row.total,
                "accuracy": round(int(row.correct or 0) / max(row.total, 1) * 100, 1),
            }
            for row in spec_stats
        ]

        # --- Performance by band ---
        band_stats = db.query(
            Question.nhs_band,
            func.count(UserAnswer.id).label("total"),
            func.sum(case((UserAnswer.is_correct == True, 1), else_=0)).label("correct"),
        ).join(Question, UserAnswer.question_id == Question.id).filter(
            UserAnswer.answered_at >= period_start,
        ).group_by(Question.nhs_band).all()

        data["band_performance"] = [
            {
                "band": row.nhs_band,
                "answers": row.total,
                "accuracy": round(int(row.correct or 0) / max(row.total, 1) * 100, 1),
            }
            for row in band_stats
        ]

        # --- Security events (din audit logs DB) ---
        try:
            from models.security import SecurityEvent
            sec_count = db.query(func.count(SecurityEvent.id)).filter(
                SecurityEvent.timestamp >= period_start
            ).scalar() or 0
            high_sev = db.query(func.count(SecurityEvent.id)).filter(
                SecurityEvent.timestamp >= period_start,
                SecurityEvent.severity.in_(["HIGH", "CRITICAL"]),
            ).scalar() or 0
            data["security_events"] = sec_count
            data["high_severity_events"] = high_sev
        except Exception:
            data["security_events"] = 0
            data["high_severity_events"] = 0

        # --- RAG Hub stats ---
        try:
            from services.rag_hub import rag_hub
            rag_stats = rag_hub.get_stats()
            data["rag_faiss_available"] = rag_stats.get("faiss", {}).get("available", False)
            data["rag_questions_indexed"] = rag_stats.get("chromadb", {}).get("questions_indexed", 0)
        except Exception:
            data["rag_faiss_available"] = False
            data["rag_questions_indexed"] = 0

        return data

    def _build_analysis_prompt(self, data: Dict[str, Any], days: int) -> str:
        """Construieste promptul structurat pentru Ollama"""
        hard_q_text = "\n".join(
            f"  - Q#{q['id']}: \"{q['title']}\" ({q['band']}, {q['specialty']}) - {q['accuracy']}% accuracy"
            for q in data.get("hardest_questions", [])[:5]
        ) or "  None detected"

        easy_q_text = "\n".join(
            f"  - Q#{q['id']}: \"{q['title']}\" ({q['band']}) - {q['accuracy']}% accuracy"
            for q in data.get("easiest_questions", [])[:5]
        ) or "  None detected"

        spec_text = "\n".join(
            f"  - {s['specialty']}: {s['answers']} answers, {s['accuracy']}% accuracy"
            for s in sorted(data.get("specialty_performance", []), key=lambda x: -x["answers"])[:10]
        ) or "  No data"

        band_text = "\n".join(
            f"  - {b['band']}: {b['answers']} answers, {b['accuracy']}% accuracy"
            for b in data.get("band_performance", [])
        ) or "  No data"

        return f"""You are an AI analyst for a UK healthcare nursing training platform used by NHS professionals.
Analyze the following platform data from the last {days} days and provide actionable insights.

PLATFORM DATA:
- Total registered users: {data.get('total_users', 0)}
- Active users (account active): {data.get('active_users', 0)}
- New users this period: {data.get('new_users', 0)}
- Users who answered questions this period: {data.get('active_learners', 0)}
- Users by role: {json.dumps(data.get('users_by_role', {}))}
- Users by subscription tier: {json.dumps(data.get('users_by_tier', {}))}

LEARNING ACTIVITY:
- Questions answered: {data.get('questions_answered', 0)}
- Correct answers: {data.get('correct_answers', 0)}
- Average accuracy: {data.get('avg_accuracy_pct', 0)}%
- Training sessions started: {data.get('training_sessions', 0)}
- Training sessions completed: {data.get('completed_sessions', 0)}
- Average session score: {data.get('avg_session_score', 0)}%

HARDEST QUESTIONS (< 40% accuracy, min 5 attempts):
{hard_q_text}

EASIEST QUESTIONS (> 95% accuracy):
{easy_q_text}

PERFORMANCE BY SPECIALTY:
{spec_text}

PERFORMANCE BY NHS BAND:
{band_text}

KNOWLEDGE BASE & RAG:
- FAISS index available: {data.get('rag_faiss_available', False)}
- Questions indexed in ChromaDB: {data.get('rag_questions_indexed', 0)}

SECURITY:
- Security events: {data.get('security_events', 0)}
- High/Critical severity events: {data.get('high_severity_events', 0)}

Respond ONLY with a valid JSON object (no markdown, no explanation outside JSON):
{{
  "summary": "2-3 sentence overview of platform health and key findings",
  "insights": [
    {{"category": "content|users|engagement|security|performance", "finding": "specific finding", "severity": "info|warning|critical"}}
  ],
  "recommendations": [
    {{"action": "specific actionable recommendation", "priority": "high|medium|low", "category": "content|users|security|performance"}}
  ],
  "question_quality_flags": [
    {{"question_id": 123, "issue": "too hard/too easy/unclear", "suggestion": "what to do"}}
  ],
  "engagement_trends": {{
    "direction": "up|down|stable",
    "key_driver": "main factor behind the trend",
    "completion_rate_pct": {round(data.get('completed_sessions', 0) / max(data.get('training_sessions', 0), 1) * 100, 1)}
  }}
}}"""

    async def _call_ollama(self, prompt: str) -> str:
        """Trimite prompt la Ollama API si returneaza raspunsul"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 4096,
                    },
                },
            )
            response.raise_for_status()
            return response.json().get("response", "")

    def _parse_response(self, raw: str) -> Dict[str, Any]:
        """Parseaza raspunsul JSON de la Ollama, cu fallback"""
        # Incearca direct
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Cauta JSON intre { si }
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                pass

        # Fallback - salveaza raw ca insight text
        return {
            "summary": "AI response could not be parsed as JSON.",
            "insights": [{"category": "system", "finding": raw[:500], "severity": "info"}],
            "recommendations": [],
            "question_quality_flags": [],
            "engagement_trends": {"direction": "unknown", "key_driver": "parse_error"},
        }

    def get_latest_insights(self, db: Session, limit: int = 10) -> List[Dict]:
        """Returneaza ultimele rapoarte din DB"""
        rows = db.query(AIInsight).order_by(
            AIInsight.generated_at.desc()
        ).limit(limit).all()

        return [
            {
                "id": r.id,
                "report_type": r.report_type,
                "status": r.status,
                "model_used": r.model_used,
                "generation_time_seconds": r.generation_time_seconds,
                "analysis_period_start": r.analysis_period_start.isoformat() if r.analysis_period_start else None,
                "analysis_period_end": r.analysis_period_end.isoformat() if r.analysis_period_end else None,
                "insights": r.insights,
                "recommendations": r.recommendations,
                "error_message": r.error_message,
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            }
            for r in rows
        ]

    def get_insight_by_id(self, db: Session, insight_id: int) -> Optional[Dict]:
        """Returneaza un raport specific"""
        r = db.query(AIInsight).filter(AIInsight.id == insight_id).first()
        if not r:
            return None
        return {
            "id": r.id,
            "report_type": r.report_type,
            "status": r.status,
            "model_used": r.model_used,
            "generation_time_seconds": r.generation_time_seconds,
            "prompt_tokens": r.prompt_tokens,
            "completion_tokens": r.completion_tokens,
            "analysis_period_start": r.analysis_period_start.isoformat() if r.analysis_period_start else None,
            "analysis_period_end": r.analysis_period_end.isoformat() if r.analysis_period_end else None,
            "insights": r.insights,
            "recommendations": r.recommendations,
            "raw_response": r.raw_response,
            "error_message": r.error_message,
            "generated_at": r.generated_at.isoformat() if r.generated_at else None,
        }


# Singleton
ollama_brain = OllamaBrainService()
