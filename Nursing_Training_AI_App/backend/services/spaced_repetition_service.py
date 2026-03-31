"""
Spaced Repetition Service - Algoritm adaptiv de selectie intrebari
Selecteaza intrebarile optime pentru fiecare user bazat pe:
- Performanta anterioara (intrebari gresite revin mai des)
- Timp de la ultima vizualizare (SM-2 inspired intervals)
- Arii slabe (specialty/band unde accuracy e scazuta)
- Varietate (nu repeta aceleasi intrebari consecutiv)
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from sqlalchemy import func, case, and_, or_, not_
from sqlalchemy.orm import Session

from models.training import Question, UserAnswer, QuestionType
from models.learning_profile import UserLearningProfile


# SM-2 inspired intervals (in zile)
# Dupa raspuns corect: interval creste
# Dupa raspuns gresit: interval revine la 1 zi
INTERVALS = [1, 3, 7, 14, 30, 60]  # zile


class SpacedRepetitionService:

    def get_next_questions(
        self,
        db: Session,
        user_id: int,
        count: int = 10,
        specialty: Optional[str] = None,
        band: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Selecteaza urmatoarele intrebari optime pentru user"""

        # 1. Intrebari gresite recent (prioritate maxima - revin in 1 zi)
        wrong_questions = self._get_wrong_questions(db, user_id, count, specialty, band)

        # 2. Intrebari din arii slabe (priority alta)
        weak_area_questions = self._get_weak_area_questions(db, user_id, count, specialty, band)

        # 3. Intrebari noi (niciodata vazute)
        new_questions = self._get_new_questions(db, user_id, count, specialty, band)

        # 4. Intrebari pentru review (vazute dar intervalul a expirat)
        review_questions = self._get_review_questions(db, user_id, count, specialty, band)

        # Combina cu prioritati: 40% wrong, 20% weak, 20% new, 20% review
        selected = []
        seen_ids = set()

        for source, ratio in [
            (wrong_questions, 0.4),
            (weak_area_questions, 0.2),
            (new_questions, 0.2),
            (review_questions, 0.2),
        ]:
            target = max(1, int(count * ratio))
            for q in source:
                if q["id"] not in seen_ids and len(selected) < count:
                    seen_ids.add(q["id"])
                    selected.append(q)
                    if len([s for s in selected if s.get("source_reason") == q.get("source_reason")]) >= target:
                        break

        # Daca nu avem destule, completam cu new questions
        if len(selected) < count:
            for q in new_questions + review_questions + weak_area_questions:
                if q["id"] not in seen_ids:
                    seen_ids.add(q["id"])
                    selected.append(q)
                    if len(selected) >= count:
                        break

        return selected[:count]

    def _get_wrong_questions(
        self, db: Session, user_id: int, count: int,
        specialty: Optional[str], band: Optional[str]
    ) -> List[Dict]:
        """Intrebari gresite in ultimele 7 zile - trebuie revizitate"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        query = db.query(
            Question.id,
            Question.title,
            Question.question_text,
            Question.question_type,
            Question.difficulty_level,
            Question.nhs_band,
            Question.specialization,
            func.max(UserAnswer.answered_at).label("last_seen"),
            func.count(UserAnswer.id).label("wrong_count"),
        ).join(
            UserAnswer, and_(
                UserAnswer.question_id == Question.id,
                UserAnswer.user_id == user_id,
                UserAnswer.is_correct == False,
            )
        ).filter(
            Question.is_active == True,
            UserAnswer.answered_at >= cutoff,
        )

        if specialty:
            query = query.filter(Question.specialization == specialty)
        if band:
            query = query.filter(Question.nhs_band == band)

        rows = query.group_by(
            Question.id, Question.title, Question.question_text,
            Question.question_type, Question.difficulty_level,
            Question.nhs_band, Question.specialization,
        ).order_by(func.count(UserAnswer.id).desc()).limit(count).all()

        return [self._format_question(r, "wrong_recently") for r in rows]

    def _get_weak_area_questions(
        self, db: Session, user_id: int, count: int,
        specialty: Optional[str], band: Optional[str]
    ) -> List[Dict]:
        """Intrebari din specialitatile unde user-ul are accuracy scazuta"""
        # Gaseste specialty cu accuracy < 60%
        profile = db.query(UserLearningProfile).filter(
            UserLearningProfile.user_id == user_id
        ).first()

        weak_specialties = []
        if profile and profile.specialty_scores:
            weak_specialties = [
                spec for spec, score in profile.specialty_scores.items()
                if score < 60
            ]

        if not weak_specialties:
            return []

        # Override cu specialty filter daca e dat
        if specialty:
            if specialty in weak_specialties:
                weak_specialties = [specialty]
            else:
                return []

        # Intrebari din aceste specialitati pe care nu le-a vazut recent
        cutoff = datetime.now(timezone.utc) - timedelta(days=3)

        # Subquery: IDs of questions answered recently
        recent_ids = db.query(UserAnswer.question_id).filter(
            UserAnswer.user_id == user_id,
            UserAnswer.answered_at >= cutoff,
        ).subquery()

        query = db.query(Question).filter(
            Question.is_active == True,
            Question.specialization.in_(weak_specialties),
            ~Question.id.in_(db.query(recent_ids)),
        )
        if band:
            query = query.filter(Question.nhs_band == band)

        questions = query.order_by(func.random()).limit(count).all()

        return [
            {
                "id": q.id,
                "title": q.title,
                "question_text": q.question_text,
                "question_type": q.question_type.value if q.question_type else None,
                "difficulty": q.difficulty_level.value if q.difficulty_level else None,
                "band": q.nhs_band,
                "specialty": q.specialization,
                "source_reason": "weak_area",
            }
            for q in questions
        ]

    def _get_new_questions(
        self, db: Session, user_id: int, count: int,
        specialty: Optional[str], band: Optional[str]
    ) -> List[Dict]:
        """Intrebari pe care user-ul nu le-a vazut niciodata"""
        # Subquery: toate question_ids pe care user-ul le-a raspuns
        answered_ids = db.query(UserAnswer.question_id).filter(
            UserAnswer.user_id == user_id,
        ).distinct().subquery()

        query = db.query(Question).filter(
            Question.is_active == True,
            ~Question.id.in_(db.query(answered_ids)),
        )
        if specialty:
            query = query.filter(Question.specialization == specialty)
        if band:
            query = query.filter(Question.nhs_band == band)

        questions = query.order_by(func.random()).limit(count).all()

        return [
            {
                "id": q.id,
                "title": q.title,
                "question_text": q.question_text,
                "question_type": q.question_type.value if q.question_type else None,
                "difficulty": q.difficulty_level.value if q.difficulty_level else None,
                "band": q.nhs_band,
                "specialty": q.specialization,
                "source_reason": "new",
            }
            for q in questions
        ]

    def _get_review_questions(
        self, db: Session, user_id: int, count: int,
        specialty: Optional[str], band: Optional[str]
    ) -> List[Dict]:
        """Intrebari corecte dar intervalul de review a expirat"""
        # Gaseste intrebari cu raspuns corect unde intervalul a trecut
        # Intervalul depinde de cate ori a fost raspunsa corect consecutiv

        query = db.query(
            Question.id,
            Question.title,
            Question.question_text,
            Question.question_type,
            Question.difficulty_level,
            Question.nhs_band,
            Question.specialization,
            func.max(UserAnswer.answered_at).label("last_seen"),
            func.sum(case((UserAnswer.is_correct == True, 1), else_=0)).label("correct_streak"),
        ).join(
            UserAnswer, and_(
                UserAnswer.question_id == Question.id,
                UserAnswer.user_id == user_id,
            )
        ).filter(
            Question.is_active == True,
        )

        if specialty:
            query = query.filter(Question.specialization == specialty)
        if band:
            query = query.filter(Question.nhs_band == band)

        rows = query.group_by(
            Question.id, Question.title, Question.question_text,
            Question.question_type, Question.difficulty_level,
            Question.nhs_band, Question.specialization,
        ).all()

        now = datetime.now(timezone.utc)
        due_for_review = []

        for r in rows:
            if not r.last_seen:
                continue
            streak = int(r.correct_streak or 0)
            interval_idx = min(streak, len(INTERVALS) - 1)
            interval_days = INTERVALS[interval_idx]

            last_seen = r.last_seen
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)

            next_review = last_seen + timedelta(days=interval_days)
            if now >= next_review:
                due_for_review.append(self._format_question(r, "review_due"))

        # Sort by most overdue first
        return due_for_review[:count]

    def get_session_plan(
        self,
        db: Session,
        user_id: int,
        session_length: int = 10,
        specialty: Optional[str] = None,
        band: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Genereaza un plan de sesiune cu mix optimal de intrebari"""
        questions = self.get_next_questions(db, user_id, session_length, specialty, band)

        # Statistici plan
        reasons = {}
        for q in questions:
            reason = q.get("source_reason", "unknown")
            reasons[reason] = reasons.get(reason, 0) + 1

        return {
            "session_length": len(questions),
            "questions": questions,
            "mix": reasons,
            "specialty_filter": specialty,
            "band_filter": band,
        }

    def _format_question(self, row, reason: str) -> Dict:
        return {
            "id": row.id,
            "title": row.title,
            "question_text": row.question_text,
            "question_type": row.question_type.value if row.question_type else None,
            "difficulty": row.difficulty_level.value if row.difficulty_level else None,
            "band": row.nhs_band,
            "specialty": row.specialization,
            "source_reason": reason,
        }


# Singleton
spaced_repetition = SpacedRepetitionService()
