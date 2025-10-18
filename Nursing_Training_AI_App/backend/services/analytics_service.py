"""
Analytics Service for Nursing Training AI
Tracks and analyzes user performance, engagement, and content effectiveness
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import json

class AnalyticsService:
    """Service for tracking and analyzing platform metrics"""
    
    def __init__(self):
        self.metrics_cache = {}
    
    # USER ANALYTICS
    
    def track_user_activity(
        self,
        user_id: str,
        activity_type: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Track user activity event"""
        event = {
            "user_id": user_id,
            "activity_type": activity_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # TODO: Save to database
        # TODO: Update real-time metrics
        
        return event
    
    def get_user_analytics(
        self,
        user_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a user"""
        
        # Set default date range (last 30 days)
        if not date_from:
            date_from = datetime.now() - timedelta(days=30)
        if not date_to:
            date_to = datetime.now()
        
        # TODO: Fetch from database
        # Mock data for now
        analytics = {
            "user_id": user_id,
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat(),
                "days": (date_to - date_from).days
            },
            "overall_stats": {
                "questions_completed": 247,
                "questions_correct": 203,
                "accuracy_percentage": 82.2,
                "time_spent_minutes": 1850,
                "average_time_per_question_seconds": 95,
                "streak_current": 7,
                "streak_longest": 14,
                "sessions_count": 34,
                "average_session_duration_minutes": 28
            },
            "performance_by_type": {
                "multiple_choice": {"completed": 98, "correct": 85, "accuracy": 86.7},
                "scenario": {"completed": 75, "correct": 58, "accuracy": 77.3},
                "calculation": {"completed": 45, "correct": 38, "accuracy": 84.4},
                "case_study": {"completed": 20, "correct": 15, "accuracy": 75.0},
                "leadership": {"completed": 9, "correct": 7, "accuracy": 77.8}
            },
            "performance_by_specialty": {
                "amu": {"completed": 89, "accuracy": 84.3},
                "emergency": {"completed": 52, "accuracy": 79.8},
                "icu": {"completed": 67, "accuracy": 81.5},
                "maternity": {"completed": 39, "accuracy": 76.9}
            },
            "performance_by_competency": {
                "Assessment": {"score": 4.2, "questions": 85},
                "Patient Safety": {"score": 4.5, "questions": 92},
                "Leadership": {"score": 3.8, "questions": 34},
                "Communication": {"score": 4.1, "questions": 67},
                "Clinical Reasoning": {"score": 3.9, "questions": 58}
            },
            "progress_over_time": [
                {"date": "2025-10-01", "questions": 12, "accuracy": 75.0},
                {"date": "2025-10-02", "questions": 15, "accuracy": 80.0},
                {"date": "2025-10-03", "questions": 8, "accuracy": 87.5},
                # ... more daily data
            ],
            "strengths": ["Patient Safety", "Assessment", "Communication"],
            "weaknesses": ["Leadership", "Governance"],
            "recommendations": [
                "Practice more leadership scenarios",
                "Review Band 6 governance questions",
                "Focus on case studies"
            ]
        }
        
        return analytics
    
    def get_user_progress_to_next_band(self, user_id: str, current_band: str) -> Dict:
        """Calculate progress towards next band"""
        
        # Define requirements for each band
        band_requirements = {
            "band_2": {"questions": 50, "accuracy": 60, "competencies": 5},
            "band_3": {"questions": 75, "accuracy": 65, "competencies": 7},
            "band_4": {"questions": 100, "accuracy": 70, "competencies": 9},
            "band_5": {"questions": 150, "accuracy": 70, "competencies": 10},
            "band_6": {"questions": 200, "accuracy": 75, "competencies": 12},
            "band_7": {"questions": 250, "accuracy": 75, "competencies": 14},
            "band_8a": {"questions": 300, "accuracy": 80, "competencies": 15}
        }
        
        # Get user's current progress
        # TODO: Fetch from database
        current_progress = {
            "questions_completed": 130,
            "current_accuracy": 78,
            "competencies_mastered": 8
        }
        
        next_band = self._get_next_band(current_band)
        requirements = band_requirements.get(next_band, {})
        
        progress = {
            "current_band": current_band,
            "next_band": next_band,
            "requirements": requirements,
            "current_progress": current_progress,
            "percentage_complete": self._calculate_progression_percentage(
                current_progress, requirements
            ),
            "on_track": self._is_on_track(current_progress, requirements)
        }
        
        return progress
    
    # CONTENT ANALYTICS
    
    def get_question_analytics(self, question_id: str) -> Dict:
        """Get analytics for a specific question"""
        
        # TODO: Fetch from database
        analytics = {
            "question_id": question_id,
            "attempts_total": 1847,
            "attempts_correct": 1123,
            "accuracy_percentage": 60.8,
            "average_time_seconds": 87,
            "difficulty_rating": 3.4,  # 1-5 scale based on performance
            "common_wrong_answers": ["Option A", "Option C"],
            "user_feedback": {
                "helpful": 156,
                "not_helpful": 23,
                "unclear": 12
            }
        }
        
        return analytics
    
    def get_question_bank_analytics(
        self,
        sector: str,
        specialty: str,
        band: str
    ) -> Dict:
        """Get analytics for a question bank"""
        
        analytics = {
            "sector": sector,
            "specialty": specialty,
            "band": band,
            "total_questions": 247,
            "completion_rate": 68.5,
            "average_accuracy": 75.3,
            "average_time_per_question": 92,
            "most_difficult_questions": [
                {"id": "q_123", "title": "Leadership scenario", "accuracy": 45.2},
                {"id": "q_456", "title": "Governance audit", "accuracy": 52.1}
            ],
            "easiest_questions": [
                {"id": "q_789", "title": "Basic vital signs", "accuracy": 94.8},
                {"id": "q_012", "title": "Hand hygiene", "accuracy": 92.3}
            ]
        }
        
        return analytics
    
    # PLATFORM ANALYTICS
    
    def get_platform_metrics(self, date_from: datetime, date_to: datetime) -> Dict:
        """Get overall platform metrics"""
        
        metrics = {
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            },
            "users": {
                "total_users": 2847,
                "active_users": 1923,
                "new_users": 156,
                "churn_rate": 3.2
            },
            "engagement": {
                "total_questions_answered": 45829,
                "average_questions_per_user": 23.8,
                "average_session_duration_minutes": 26.5,
                "daily_active_users": 1234,
                "weekly_active_users": 1923,
                "monthly_active_users": 2456
            },
            "performance": {
                "platform_average_accuracy": 76.8,
                "average_time_per_question": 89,
                "completion_rate": 72.4
            },
            "revenue": {
                "total_revenue_gbp": 15678.50,
                "mrr": 8945.30,  # Monthly Recurring Revenue
                "arr": 107343.60,  # Annual Recurring Revenue
                "average_revenue_per_user": 5.51
            },
            "subscriptions": {
                "demo": 456,
                "basic": 1234,
                "professional": 1089,
                "enterprise": 68
            },
            "top_specialties": [
                {"name": "AMU", "users": 892, "questions": 12456},
                {"name": "Emergency", "users": 678, "questions": 9823},
                {"name": "ICU", "users": 534, "questions": 8912}
            ],
            "top_sectors": [
                {"name": "NHS", "users": 1845, "percentage": 64.8},
                {"name": "Care Homes", "users": 512, "percentage": 18.0},
                {"name": "Primary Care", "users": 345, "percentage": 12.1}
            ]
        }
        
        return metrics
    
    def get_cohort_analysis(self, cohort_type: str = "monthly") -> List[Dict]:
        """Analyze user cohorts (retention analysis)"""
        
        # TODO: Implement actual cohort analysis
        cohorts = [
            {
                "cohort": "2025-01",
                "users_joined": 234,
                "retention_month_1": 89.5,
                "retention_month_2": 76.3,
                "retention_month_3": 68.9
            },
            {
                "cohort": "2025-02",
                "users_joined": 289,
                "retention_month_1": 92.1,
                "retention_month_2": 78.5,
                "retention_month_3": 71.2
            }
        ]
        
        return cohorts
    
    # CONTENT EFFECTIVENESS
    
    def analyze_content_effectiveness(self) -> Dict:
        """Analyze which questions and topics are most effective"""
        
        analysis = {
            "most_effective_questions": [
                {
                    "question_id": "q_001",
                    "title": "Sepsis recognition",
                    "learning_improvement": 85.3,  # % improvement after answering
                    "user_satisfaction": 4.7
                }
            ],
            "least_effective_questions": [
                {
                    "question_id": "q_456",
                    "title": "Complex governance scenario",
                    "learning_improvement": 12.5,
                    "user_satisfaction": 2.3,
                    "needs_revision": True
                }
            ],
            "topics_needing_improvement": [
                {"topic": "Governance", "avg_accuracy": 54.2},
                {"topic": "Leadership", "avg_accuracy": 62.8}
            ],
            "high_performing_topics": [
                {"topic": "Patient Safety", "avg_accuracy": 88.9},
                {"topic": "Basic Assessment", "avg_accuracy": 86.5}
            ]
        }
        
        return analysis
    
    # HELPER METHODS
    
    def _get_next_band(self, current_band: str) -> str:
        """Get next band in progression"""
        band_progression = {
            "band_2": "band_3",
            "band_3": "band_4",
            "band_4": "band_5",
            "band_5": "band_6",
            "band_6": "band_7",
            "band_7": "band_8a",
            "band_8a": "band_8b",
            "band_8b": "band_8c",
            "band_8c": "band_8d",
            "band_8d": "band_8d"  # No further progression
        }
        return band_progression.get(current_band, current_band)
    
    def _calculate_progression_percentage(
        self,
        current: Dict,
        requirements: Dict
    ) -> float:
        """Calculate percentage progress to next band"""
        
        if not requirements:
            return 100.0
        
        # Calculate progress for each requirement
        questions_progress = min(100, (current["questions_completed"] / requirements["questions"]) * 100)
        accuracy_progress = min(100, (current["current_accuracy"] / requirements["accuracy"]) * 100)
        competency_progress = min(100, (current["competencies_mastered"] / requirements["competencies"]) * 100)
        
        # Weight the progress (questions 40%, accuracy 40%, competencies 20%)
        weighted_progress = (
            (questions_progress * 0.4) +
            (accuracy_progress * 0.4) +
            (competency_progress * 0.2)
        )
        
        return round(weighted_progress, 1)
    
    def _is_on_track(self, current: Dict, requirements: Dict) -> bool:
        """Determine if user is on track to progress"""
        if not requirements:
            return True
        
        # Check if user meets at least 60% of each requirement
        questions_ok = current["questions_completed"] >= (requirements["questions"] * 0.6)
        accuracy_ok = current["current_accuracy"] >= (requirements["accuracy"] * 0.95)
        competency_ok = current["competencies_mastered"] >= (requirements["competencies"] * 0.6)
        
        return questions_ok and accuracy_ok and competency_ok
    
    # EXPORT FUNCTIONS
    
    def export_user_report_data(
        self,
        user_id: str,
        date_from: datetime,
        date_to: datetime
    ) -> Dict:
        """Export user report data for PDF/Excel generation"""
        
        analytics = self.get_user_analytics(user_id, date_from, date_to)
        
        export_data = {
            "report_generated": datetime.now().isoformat(),
            "user_id": user_id,
            "period": analytics["period"],
            "summary": {
                "total_questions": analytics["overall_stats"]["questions_completed"],
                "accuracy": analytics["overall_stats"]["accuracy_percentage"],
                "time_spent_hours": round(analytics["overall_stats"]["time_spent_minutes"] / 60, 1),
                "current_streak": analytics["overall_stats"]["streak_current"]
            },
            "performance_breakdown": analytics["performance_by_type"],
            "specialty_performance": analytics["performance_by_specialty"],
            "competency_scores": analytics["performance_by_competency"],
            "progress_chart_data": analytics["progress_over_time"],
            "strengths": analytics["strengths"],
            "areas_for_improvement": analytics["weaknesses"],
            "recommendations": analytics["recommendations"]
        }
        
        return export_data
    
    def generate_weekly_summary(self, user_id: str) -> Dict:
        """Generate weekly summary for email notification"""
        
        week_start = datetime.now() - timedelta(days=7)
        week_end = datetime.now()
        
        analytics = self.get_user_analytics(user_id, week_start, week_end)
        
        summary = {
            "week_ending": week_end.strftime("%d %B %Y"),
            "highlights": {
                "questions_this_week": analytics["overall_stats"]["questions_completed"],
                "accuracy_this_week": analytics["overall_stats"]["accuracy_percentage"],
                "time_spent_minutes": analytics["overall_stats"]["time_spent_minutes"],
                "streak_maintained": analytics["overall_stats"]["streak_current"] >= 7,
                "improvement_from_last_week": "+5.2%"  # TODO: Calculate actual improvement
            },
            "achievements_unlocked": [
                "🔥 7 Day Streak",
                "💯 100 Questions Milestone"
            ],
            "top_performing_area": "Patient Safety (92% accuracy)",
            "focus_area_next_week": "Leadership scenarios",
            "recommended_actions": analytics["recommendations"][:3]
        }
        
        return summary
    
    # LEADERBOARD ANALYTICS
    
    def get_leaderboard(
        self,
        scope: str = "global",  # global, specialty, sector, band
        filter_by: Optional[Dict] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get leaderboard rankings"""
        
        # TODO: Fetch from database and calculate rankings
        leaderboard = [
            {
                "rank": 1,
                "user_name": "Sarah J.",
                "band": "Band 6",
                "specialty": "Emergency",
                "score": 2456,
                "accuracy": 91.5,
                "streak": 28,
                "avatar": "👩‍⚕️"
            },
            {
                "rank": 2,
                "user_name": "Michael T.",
                "band": "Band 5",
                "specialty": "ICU",
                "score": 2234,
                "accuracy": 89.3,
                "streak": 21,
                "avatar": "👨‍⚕️"
            },
            # ... more users
        ]
        
        return leaderboard[:limit]
    
    # TEAM ANALYTICS (Enterprise)
    
    def get_team_analytics(
        self,
        organization_id: str,
        date_from: datetime,
        date_to: datetime
    ) -> Dict:
        """Get analytics for an entire organization (Enterprise plan)"""
        
        analytics = {
            "organization_id": organization_id,
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            },
            "team_stats": {
                "total_members": 45,
                "active_members": 38,
                "engagement_rate": 84.4,
                "average_accuracy": 78.5,
                "total_questions_completed": 3456,
                "total_training_hours": 289
            },
            "performance_distribution": {
                "excellent": 12,  # >90%
                "very_good": 18,  # 80-90%
                "good": 10,  # 70-80%
                "needs_support": 5  # <70%
            },
            "top_performers": [
                {"name": "Sarah J.", "accuracy": 91.5, "questions": 234},
                {"name": "Michael T.", "accuracy": 89.3, "questions": 198}
            ],
            "members_needing_support": [
                {"name": "Emma W.", "accuracy": 65.2, "questions": 45},
                {"name": "David L.", "accuracy": 68.9, "questions": 67}
            ],
            "competency_gaps": [
                {"competency": "Leadership", "average_score": 3.2},
                {"competency": "Governance", "average_score": 3.5}
            ],
            "training_completion_by_band": {
                "band_5": {"members": 20, "completion_rate": 78.5},
                "band_6": {"members": 15, "completion_rate": 82.3},
                "band_7": {"members": 10, "completion_rate": 76.9}
            }
        }
        
        return analytics
    
    # REAL-TIME METRICS
    
    def get_realtime_metrics(self) -> Dict:
        """Get real-time platform metrics"""
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "active_now": {
                "users_online": 234,
                "questions_being_answered": 89,
                "active_sessions": 198
            },
            "today": {
                "questions_completed": 4567,
                "new_registrations": 23,
                "active_users": 1234
            },
            "system_health": {
                "api_response_time_ms": 145,
                "database_query_time_ms": 23,
                "error_rate": 0.02,
                "uptime_percentage": 99.98
            }
        }
        
        return metrics

# Singleton instance
analytics_service = AnalyticsService()

