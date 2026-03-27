"""
GDPR Compliance Service
Handles GDPR rights: access, erasure, portability
Uses real SQLAlchemy queries against the database.
"""

from typing import Dict, List, Any
from datetime import datetime, timezone
import json
from sqlalchemy.orm import Session

from models.user import User, UserProgress, UserSession
from models.training import UserAnswer, TrainingSession, UserLearningPath


class GDPRService:
    """Service for GDPR compliance with real database operations"""

    def __init__(self):
        self.retention_period_days = 2555  # 7 ani pentru date medicale

    # ========================================
    # RIGHT TO ACCESS (Article 15) - Colectare date reale
    # ========================================

    def collect_all_user_data(self, user: User, db: Session) -> Dict[str, Any]:
        """Colecteaza TOATE datele unui utilizator din DB pentru export GDPR"""

        # Progres
        progress_records = db.query(UserProgress).filter(UserProgress.user_id == user.id).all()
        progress_data = [
            {
                "band": p.current_band.value if p.current_band else None,
                "progress_pct": p.band_progress_percentage,
                "questions_answered": p.total_questions_answered,
                "correct_answers": p.correct_answers,
                "study_time_minutes": p.total_study_time_minutes,
                "clinical_score": p.clinical_skills_score,
                "management_score": p.management_skills_score,
                "communication_score": p.communication_skills_score,
            }
            for p in progress_records
        ]

        # Raspunsuri la intrebari
        answers = db.query(UserAnswer).filter(UserAnswer.user_id == user.id).all()
        answers_data = [
            {
                "question_id": a.question_id,
                "answer": a.user_answer,
                "is_correct": a.is_correct,
                "confidence": a.confidence_level,
                "time_seconds": a.time_taken_seconds,
                "ai_feedback": a.ai_feedback,
                "answered_at": a.answered_at.isoformat() if a.answered_at else None,
            }
            for a in answers
        ]

        # Sesiuni de training
        sessions = db.query(TrainingSession).filter(TrainingSession.user_id == user.id).all()
        sessions_data = [
            {
                "id": s.id,
                "band": s.nhs_band,
                "specialization": s.specialization,
                "total_questions": s.total_questions,
                "correct": s.correct_answers,
                "score_pct": s.score_percentage,
                "duration_min": s.duration_minutes,
                "completed": s.is_completed,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in sessions
        ]

        # Sesiuni de login
        login_sessions = db.query(UserSession).filter(UserSession.user_id == user.id).all()
        login_data = [
            {
                "ip_address": ls.ip_address,
                "device_type": ls.device_type,
                "created_at": ls.created_at.isoformat() if ls.created_at else None,
                "last_activity": ls.last_activity.isoformat() if ls.last_activity else None,
            }
            for ls in login_sessions
        ]

        # Learning paths
        learning_paths = db.query(UserLearningPath).filter(UserLearningPath.user_id == user.id).all()
        lp_data = [
            {
                "learning_path_id": lp.learning_path_id,
                "current_module": lp.current_module,
                "progress_pct": lp.progress_percentage,
                "completed": lp.is_completed,
                "started_at": lp.started_at.isoformat() if lp.started_at else None,
            }
            for lp in learning_paths
        ]

        return {
            "export_generated_at": datetime.now(timezone.utc).isoformat(),
            "gdpr_article": "Article 15 - Right of access",
            "user_id": user.id,
            "personal_information": {
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value if user.role else None,
                "nhs_band": user.nhs_band.value if user.nhs_band else None,
                "specialization": user.specialization,
                "years_experience": user.years_experience,
                "preferred_language": user.preferred_language,
                "timezone": user.timezone,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            },
            "subscription": {
                "tier": user.subscription_tier.value if user.subscription_tier else "demo",
                "expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
                "demo_questions_used": user.demo_questions_used,
                "demo_questions_limit": user.demo_questions_limit,
            },
            "training_progress": progress_data,
            "answers_submitted": {
                "count": len(answers_data),
                "records": answers_data,
            },
            "training_sessions": {
                "count": len(sessions_data),
                "records": sessions_data,
            },
            "learning_paths": lp_data,
            "login_sessions": {
                "count": len(login_data),
                "records": login_data,
            },
            "data_processing_purposes": [
                "Provide healthcare training services",
                "Track learning progress and performance",
                "Process subscription payments",
                "Send service notifications",
                "Improve training content quality",
            ],
            "data_recipients": [
                "Nursing Training AI platform (internal)",
                "Stripe (payment processor, if subscribed)",
                "Cloud hosting provider",
            ],
            "data_retention_policy": f"{self.retention_period_days} days (7 years, healthcare requirement)",
            "your_rights": [
                "Right to access (this export)",
                "Right to erasure (Article 17)",
                "Right to data portability (Article 20)",
                "Right to rectification (Article 16)",
                "Right to restrict processing (Article 18)",
                "Right to object (Article 21)",
            ],
        }

    # ========================================
    # RIGHT TO ERASURE (Article 17) - Stergere reala
    # ========================================

    def delete_all_user_data(self, user: User, db: Session) -> Dict[str, Any]:
        """
        Sterge PERMANENT toate datele unui utilizator din DB.
        Conform GDPR Article 17 - Right to be forgotten.
        Aceasta operatie este IREVERSIBILA.
        """
        user_id = user.id
        deleted_counts = {}

        # 1. Stergere raspunsuri
        count = db.query(UserAnswer).filter(UserAnswer.user_id == user_id).delete()
        deleted_counts["user_answers"] = count

        # 2. Stergere sesiuni training
        count = db.query(TrainingSession).filter(TrainingSession.user_id == user_id).delete()
        deleted_counts["training_sessions"] = count

        # 3. Stergere learning paths
        count = db.query(UserLearningPath).filter(UserLearningPath.user_id == user_id).delete()
        deleted_counts["user_learning_paths"] = count

        # 4. Stergere progres (cascade ar trebui sa acopere, dar explicit e mai sigur)
        count = db.query(UserProgress).filter(UserProgress.user_id == user_id).delete()
        deleted_counts["user_progress"] = count

        # 5. Stergere sesiuni login
        count = db.query(UserSession).filter(UserSession.user_id == user_id).delete()
        deleted_counts["user_sessions"] = count

        # 6. Stergere cont utilizator
        db.query(User).filter(User.id == user_id).delete()
        deleted_counts["users"] = 1

        db.commit()

        return {
            "gdpr_article": "Article 17 - Right to erasure",
            "user_id": user_id,
            "deleted_at": datetime.now(timezone.utc).isoformat(),
            "deleted_records": deleted_counts,
            "total_records_deleted": sum(deleted_counts.values()),
            "status": "completed",
            "irreversible": True,
        }


# Singleton
gdpr_service = GDPRService()
