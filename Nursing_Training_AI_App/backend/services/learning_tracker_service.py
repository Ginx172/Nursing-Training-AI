"""
Learning Tracker Service - Urmareste evolutia fiecarui user
Stabileste baseline, calculeaza trend, genereaza recomandari personalizate.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any

from sqlalchemy import func, case, cast, Date
from sqlalchemy.orm import Session

from models.user import User, UserProgress, NHSBand
from models.training import Question, UserAnswer, TrainingSession
from models.learning_profile import UserLearningProfile, LearningEvent

BASELINE_THRESHOLD = 20  # Numar intrebari necesare pt baseline


class LearningTrackerService:

    def record_answer(
        self,
        db: Session,
        user_id: int,
        question_id: int,
        is_correct: bool,
        time_taken_seconds: Optional[int] = None,
    ) -> None:
        """Inregistreaza un raspuns si actualizeaza profilul user-ului"""
        # Salveaza evenimentul
        event = LearningEvent(
            user_id=user_id,
            event_type="answer",
            question_id=question_id,
            is_correct=is_correct,
            time_taken_seconds=time_taken_seconds,
        )
        db.add(event)

        # Get or create profil
        profile = db.query(UserLearningProfile).filter(
            UserLearningProfile.user_id == user_id
        ).first()

        if not profile:
            profile = UserLearningProfile(user_id=user_id)
            db.add(profile)
            db.flush()

        # Actualizeaza totals
        profile.total_questions_answered += 1
        if is_correct:
            profile.total_correct += 1
        profile.current_accuracy_pct = round(
            profile.total_correct / max(profile.total_questions_answered, 1) * 100, 1
        )

        # Baseline logic
        if profile.total_questions_answered <= BASELINE_THRESHOLD:
            profile.baseline_questions = profile.total_questions_answered
            if profile.total_questions_answered == BASELINE_THRESHOLD:
                profile.baseline_accuracy_pct = profile.current_accuracy_pct
                profile.baseline_established_at = datetime.now(timezone.utc)

        # Recalculeaza trend + strengths/weaknesses periodic (la fiecare 10 raspunsuri)
        if profile.total_questions_answered % 10 == 0:
            self._update_trend(db, profile)
            self._update_strengths_weaknesses(db, profile, user_id)
            self._update_learning_velocity(db, profile, user_id)

        db.commit()

    def get_user_profile(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Returneaza profilul complet de invatare al user-ului"""
        profile = db.query(UserLearningProfile).filter(
            UserLearningProfile.user_id == user_id
        ).first()

        if not profile:
            return {
                "exists": False,
                "message": "No learning profile yet. Start answering questions to build your profile.",
                "total_questions_answered": 0,
            }

        # User info
        user = db.query(User).filter(User.id == user_id).first()

        return {
            "exists": True,
            "user_id": user_id,
            "nhs_band": user.nhs_band.value if user and user.nhs_band else None,
            "baseline": {
                "established": profile.baseline_accuracy_pct is not None,
                "accuracy_pct": profile.baseline_accuracy_pct,
                "established_at": profile.baseline_established_at.isoformat() if profile.baseline_established_at else None,
                "questions_needed": max(0, BASELINE_THRESHOLD - profile.total_questions_answered),
            },
            "current": {
                "accuracy_pct": profile.current_accuracy_pct,
                "total_questions": profile.total_questions_answered,
                "total_correct": profile.total_correct,
            },
            "improvement": round(
                (profile.current_accuracy_pct or 0) - (profile.baseline_accuracy_pct or 0), 1
            ) if profile.baseline_accuracy_pct else None,
            "trend": profile.trend,
            "learning_velocity": profile.learning_velocity,
            "strengths": {
                "specialty": profile.strongest_specialty,
                "competency": profile.strongest_competency,
            },
            "weaknesses": {
                "specialty": profile.weakest_specialty,
                "competency": profile.weakest_competency,
            },
            "specialty_scores": profile.specialty_scores or {},
            "competency_scores": profile.competency_scores or {},
            "recommendations": profile.recommendations or [],
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }

    def generate_recommendations(self, db: Session, user_id: int) -> List[Dict]:
        """Genereaza recomandari personalizate bazate pe slabiciunile reale"""
        profile = db.query(UserLearningProfile).filter(
            UserLearningProfile.user_id == user_id
        ).first()
        if not profile or profile.total_questions_answered < BASELINE_THRESHOLD:
            return [{"action": f"Answer {BASELINE_THRESHOLD - (profile.total_questions_answered if profile else 0)} more questions to establish your baseline and get personalized recommendations.", "priority": "high", "category": "onboarding"}]

        recommendations = []
        specialty_scores = profile.specialty_scores or {}
        competency_scores = profile.competency_scores or {}

        # Specialitati cu accuracy < 60%
        for spec, acc in sorted(specialty_scores.items(), key=lambda x: x[1]):
            if acc < 60:
                recommendations.append({
                    "action": f"Focus on {spec} questions - your accuracy is {acc}%",
                    "priority": "high",
                    "category": "specialty",
                    "target": spec,
                    "current_score": acc,
                })
            elif acc < 75:
                recommendations.append({
                    "action": f"Practice more {spec} questions to strengthen this area ({acc}%)",
                    "priority": "medium",
                    "category": "specialty",
                    "target": spec,
                    "current_score": acc,
                })

        # Competente slabe (scor < 3 din UserProgress)
        user_progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
        for p in user_progress:
            if p.clinical_skills_score < 3:
                recommendations.append({
                    "action": f"Improve clinical skills for {p.current_band.value if p.current_band else 'your band'} - current score: {p.clinical_skills_score}/5",
                    "priority": "high", "category": "competency", "target": "clinical",
                })
            if p.management_skills_score < 3:
                recommendations.append({
                    "action": f"Work on management skills for {p.current_band.value if p.current_band else 'your band'} - current score: {p.management_skills_score}/5",
                    "priority": "medium", "category": "competency", "target": "management",
                })
            if p.communication_skills_score < 3:
                recommendations.append({
                    "action": f"Strengthen communication skills for {p.current_band.value if p.current_band else 'your band'} - current score: {p.communication_skills_score}/5",
                    "priority": "medium", "category": "competency", "target": "communication",
                })

        # Intrebari gresite repetat (>= 2 greseli pe aceeasi intrebare)
        repeated_wrong = db.query(
            UserAnswer.question_id,
            func.count(UserAnswer.id).label("wrong_count"),
        ).filter(
            UserAnswer.user_id == user_id,
            UserAnswer.is_correct == False,
        ).group_by(UserAnswer.question_id).having(
            func.count(UserAnswer.id) >= 2
        ).limit(5).all()

        if repeated_wrong:
            q_ids = [r.question_id for r in repeated_wrong]
            questions = db.query(Question).filter(Question.id.in_(q_ids)).all()
            q_map = {q.id: q for q in questions}
            for r in repeated_wrong:
                q = q_map.get(r.question_id)
                if q:
                    recommendations.append({
                        "action": f"Review: \"{q.title[:60]}\" - you've answered incorrectly {r.wrong_count} times",
                        "priority": "high", "category": "review",
                        "question_id": r.question_id,
                    })

        # Trend declining
        if profile.trend == "declining":
            recommendations.insert(0, {
                "action": "Your performance is declining. Consider reviewing recent weak areas and taking shorter, focused sessions.",
                "priority": "high", "category": "general",
            })

        # Salveaza recomandarile in profil
        profile.recommendations = recommendations[:15]
        profile.last_recommendation_at = datetime.now(timezone.utc)
        db.commit()

        return recommendations[:15]

    def get_progress_timeline(self, db: Session, user_id: int, days: int = 90) -> List[Dict]:
        """Date saptamanale pt graficul de evolutie"""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        weekly_data = db.query(
            func.date_trunc('week', UserAnswer.answered_at).label("week"),
            func.count(UserAnswer.id).label("total"),
            func.sum(case((UserAnswer.is_correct == True, 1), else_=0)).label("correct"),
        ).filter(
            UserAnswer.user_id == user_id,
            UserAnswer.answered_at >= start_date,
        ).group_by(
            func.date_trunc('week', UserAnswer.answered_at)
        ).order_by(
            func.date_trunc('week', UserAnswer.answered_at)
        ).all()

        timeline = []
        for row in weekly_data:
            total = row.total or 0
            correct = int(row.correct or 0)
            timeline.append({
                "week": row.week.strftime("%Y-%m-%d") if row.week else None,
                "questions": total,
                "correct": correct,
                "accuracy_pct": round(correct / max(total, 1) * 100, 1),
            })

        return timeline

    def record_event(
        self, db: Session, user_id: int, event_type: str, metadata: Optional[Dict] = None
    ) -> None:
        """Inregistreaza un eveniment generic de invatare"""
        event = LearningEvent(
            user_id=user_id,
            event_type=event_type,
            metadata=metadata,
        )
        db.add(event)
        db.commit()

    # --- Private helpers ---

    def _update_trend(self, db: Session, profile: UserLearningProfile) -> None:
        """Calculeaza trend: compara ultimele 50 raspunsuri vs precedentele 50"""
        user_id = profile.user_id

        recent_50 = db.query(
            func.count(UserAnswer.id).label("total"),
            func.sum(case((UserAnswer.is_correct == True, 1), else_=0)).label("correct"),
        ).filter(
            UserAnswer.user_id == user_id
        ).order_by(UserAnswer.answered_at.desc()).limit(50).first()

        # Luam precedentele 50 (offset 50, limit 50)
        older_answers = db.query(UserAnswer).filter(
            UserAnswer.user_id == user_id
        ).order_by(UserAnswer.answered_at.desc()).offset(50).limit(50).all()

        if not older_answers or len(older_answers) < 20:
            profile.trend = "stable"
            return

        recent_acc = (int(recent_50.correct or 0) / max(recent_50.total or 1, 1)) * 100 if recent_50 else 0
        older_correct = sum(1 for a in older_answers if a.is_correct)
        older_acc = (older_correct / len(older_answers)) * 100

        diff = recent_acc - older_acc
        if diff > 3:
            profile.trend = "improving"
        elif diff < -3:
            profile.trend = "declining"
        else:
            profile.trend = "stable"

    def _update_strengths_weaknesses(
        self, db: Session, profile: UserLearningProfile, user_id: int
    ) -> None:
        """Recalculeaza strengths/weaknesses din UserAnswer JOIN Question"""
        # Per specialty
        spec_stats = db.query(
            Question.specialization,
            func.count(UserAnswer.id).label("total"),
            func.sum(case((UserAnswer.is_correct == True, 1), else_=0)).label("correct"),
        ).join(Question, UserAnswer.question_id == Question.id).filter(
            UserAnswer.user_id == user_id,
            Question.specialization.isnot(None),
            Question.specialization != "",
        ).group_by(Question.specialization).having(
            func.count(UserAnswer.id) >= 5
        ).all()

        if spec_stats:
            spec_scores = {}
            for row in spec_stats:
                acc = round(int(row.correct or 0) / max(row.total, 1) * 100, 1)
                spec_scores[row.specialization] = acc

            profile.specialty_scores = spec_scores
            if spec_scores:
                profile.strongest_specialty = max(spec_scores, key=spec_scores.get)
                profile.weakest_specialty = min(spec_scores, key=spec_scores.get)

        # Per competency (din UserProgress)
        progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
        if progress:
            comp_totals = {"clinical": 0, "management": 0, "communication": 0}
            count = 0
            for p in progress:
                comp_totals["clinical"] += p.clinical_skills_score or 0
                comp_totals["management"] += p.management_skills_score or 0
                comp_totals["communication"] += p.communication_skills_score or 0
                count += 1
            if count:
                comp_scores = {k: round(v / count, 1) for k, v in comp_totals.items()}
                profile.competency_scores = comp_scores
                profile.strongest_competency = max(comp_scores, key=comp_scores.get)
                profile.weakest_competency = min(comp_scores, key=comp_scores.get)

    def _update_learning_velocity(
        self, db: Session, profile: UserLearningProfile, user_id: int
    ) -> None:
        """Calculeaza cate intrebari raspunde per zi (media ultimelor 30 zile)"""
        start = datetime.now(timezone.utc) - timedelta(days=30)
        count = db.query(func.count(UserAnswer.id)).filter(
            UserAnswer.user_id == user_id,
            UserAnswer.answered_at >= start,
        ).scalar() or 0
        profile.learning_velocity = round(count / 30, 1)


# Singleton
learning_tracker = LearningTrackerService()
