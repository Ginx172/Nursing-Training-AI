#!/usr/bin/env python3
"""
Personalized Recommendation Service for Nursing Training
Provides tailored learning recommendations based on user performance and band level
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class UserProfile:
    """User profile for personalized recommendations"""
    user_id: str
    current_band: str
    specialty: str
    experience_level: str
    strengths: List[str]
    weaknesses: List[str]
    learning_goals: List[str]
    preferred_learning_style: str
    time_available: int  # minutes per week
    last_activity: datetime

@dataclass
class LearningRecommendation:
    """Individual learning recommendation"""
    recommendation_id: str
    title: str
    description: str
    type: str  # question, scenario, case_study, resource, course
    difficulty: str
    estimated_time: int  # minutes
    priority: str  # high, medium, low
    rationale: str
    resources: List[str]
    prerequisites: List[str]

class PersonalizedRecommendationService:
    def __init__(self):
        self.band_progression_paths = {
            "band_2": {
                "next_band": "band_3",
                "key_skills": ["Basic clinical skills", "Patient safety", "Communication"],
                "development_areas": ["Clinical knowledge", "Assessment skills", "Teamwork"]
            },
            "band_3": {
                "next_band": "band_4", 
                "key_skills": ["Clinical skills", "Basic supervision", "Learning"],
                "development_areas": ["Leadership basics", "Quality improvement", "Mentoring"]
            },
            "band_4": {
                "next_band": "band_5",
                "key_skills": ["Clinical expertise", "Basic leadership", "Mentoring"],
                "development_areas": ["Advanced clinical", "Team leadership", "Governance"]
            },
            "band_5": {
                "next_band": "band_6",
                "key_skills": ["Clinical expertise", "Leadership", "Teaching"],
                "development_areas": ["Management skills", "Advanced governance", "Strategic thinking"]
            },
            "band_6": {
                "next_band": "band_7",
                "key_skills": ["Advanced clinical", "Team leadership", "Management"],
                "development_areas": ["Strategic leadership", "Service management", "Policy development"]
            },
            "band_7": {
                "next_band": "band_8",
                "key_skills": ["Strategic leadership", "Service management", "Policy development"],
                "development_areas": ["Executive leadership", "Organizational development", "Strategic planning"]
            },
            "band_8": {
                "next_band": "band_9",
                "key_skills": ["Strategic management", "Service development", "Policy implementation"],
                "development_areas": ["Executive leadership", "Organizational strategy", "Policy creation"]
            },
            "band_9": {
                "next_band": None,
                "key_skills": ["Executive leadership", "Strategic planning", "Organizational development"],
                "development_areas": ["Industry leadership", "Innovation", "Mentoring others"]
            }
        }
        
        self.learning_resources = {
            "clinical_skills": {
                "band_2_3": [
                    "NMC Code of Professional Practice",
                    "Basic Life Support (BLS) certification",
                    "Infection control training",
                    "Medication administration course"
                ],
                "band_4_5": [
                    "Advanced Life Support (ALS)",
                    "Clinical assessment skills course",
                    "Leadership fundamentals",
                    "Quality improvement training"
                ],
                "band_6_7": [
                    "Advanced clinical practice course",
                    "Management and leadership program",
                    "Governance and audit training",
                    "Policy development workshop"
                ],
                "band_8_9": [
                    "Executive leadership program",
                    "Strategic planning course",
                    "Organizational development training",
                    "Healthcare policy and innovation"
                ]
            },
            "specialty_specific": {
                "amu": [
                    "Acute Medical Unit protocols",
                    "NICE CG127 - Hypertension Management",
                    "NICE NG51 - Sepsis Recognition",
                    "Emergency response training"
                ],
                "cardiology": [
                    "Cardiac assessment skills",
                    "ECG interpretation course",
                    "NICE CG181 - Chest Pain",
                    "Heart failure management"
                ],
                "emergency": [
                    "Emergency triage training",
                    "Trauma management course",
                    "NICE CG176 - Head Injury Assessment",
                    "Major incident response"
                ],
                "icu": [
                    "Critical care nursing course",
                    "Ventilator management training",
                    "NICE CG50 - Recognition and Response to Acute Illness",
                    "Hemodynamic monitoring"
                ],
                "maternity": [
                    "Antenatal and postnatal care",
                    "NICE CG190 - Intrapartum Care",
                    "NICE CG62 - Antenatal Care",
                    "Newborn care specialist training"
                ],
                "mental_health": [
                    "Mental health assessment skills",
                    "NICE NG10 - Violence and Aggression Management",
                    "Therapeutic communication training",
                    "Crisis intervention techniques"
                ],
                "neurology": [
                    "Neurological assessment course",
                    "NICE CG68 - Stroke",
                    "Seizure management training",
                    "Rehabilitation principles"
                ],
                "oncology": [
                    "Cancer care specialist course",
                    "NICE CG81 - Cancer Services",
                    "Chemotherapy management training",
                    "Palliative care principles"
                ],
                "pediatrics": [
                    "Pediatric assessment skills",
                    "NICE CG160 - Fever in Under 5s",
                    "Child development knowledge",
                    "Family-centered care training"
                ]
            }
        }

    def generate_personalized_recommendations(self, user_profile: UserProfile, 
                                           performance_data: Dict[str, Any]) -> List[LearningRecommendation]:
        """Generate personalized learning recommendations based on user profile and performance"""
        recommendations = []
        
        # Analyze performance gaps
        performance_gaps = self._analyze_performance_gaps(user_profile, performance_data)
        
        # Generate recommendations for each gap
        for gap in performance_gaps:
            gap_recommendations = self._create_recommendations_for_gap(gap, user_profile)
            recommendations.extend(gap_recommendations)
        
        # Add progression recommendations
        progression_recommendations = self._create_progression_recommendations(user_profile)
        recommendations.extend(progression_recommendations)
        
        # Add specialty-specific recommendations
        specialty_recommendations = self._create_specialty_recommendations(user_profile)
        recommendations.extend(specialty_recommendations)
        
        # Prioritize recommendations
        prioritized_recommendations = self._prioritize_recommendations(recommendations, user_profile)
        
        return prioritized_recommendations

    def _analyze_performance_gaps(self, user_profile: UserProfile, 
                                performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze user performance to identify learning gaps"""
        gaps = []
        
        # Analyze question performance by type
        question_performance = performance_data.get("question_performance", {})
        for question_type, performance in question_performance.items():
            if performance.get("accuracy", 0) < 0.7:  # Below 70% accuracy
                gaps.append({
                    "type": "question_type",
                    "area": question_type,
                    "current_level": performance.get("accuracy", 0),
                    "target_level": 0.8,
                    "priority": "high" if performance.get("accuracy", 0) < 0.5 else "medium"
                })
        
        # Analyze competency performance
        competency_performance = performance_data.get("competency_performance", {})
        for competency, performance in competency_performance.items():
            if performance.get("score", 0) < 3:  # Below satisfactory level
                gaps.append({
                    "type": "competency",
                    "area": competency,
                    "current_level": performance.get("score", 0),
                    "target_level": 4,
                    "priority": "high" if performance.get("score", 0) < 2 else "medium"
                })
        
        # Analyze band-specific skills
        band_skills = self.band_progression_paths.get(user_profile.current_band, {}).get("key_skills", [])
        for skill in band_skills:
            if skill not in user_profile.strengths:
                gaps.append({
                    "type": "band_skill",
                    "area": skill,
                    "current_level": "developing",
                    "target_level": "proficient",
                    "priority": "high"
                })
        
        return gaps

    def _create_recommendations_for_gap(self, gap: Dict[str, Any], 
                                      user_profile: UserProfile) -> List[LearningRecommendation]:
        """Create specific recommendations to address a performance gap"""
        recommendations = []
        
        gap_type = gap["type"]
        area = gap["area"]
        priority = gap["priority"]
        
        if gap_type == "question_type":
            # Recommend specific question types to practice
            recommendations.append(LearningRecommendation(
                recommendation_id=f"practice_{area}_{user_profile.user_id}",
                title=f"Practice {area.replace('_', ' ').title()} Questions",
                description=f"Focus on {area} questions to improve your accuracy from {gap['current_level']:.1%} to {gap['target_level']:.1%}",
                type="question",
                difficulty=user_profile.current_band,
                estimated_time=30,
                priority=priority,
                rationale=f"Your current accuracy in {area} questions is below the recommended threshold",
                resources=[f"Enhanced question bank for {area}"],
                prerequisites=[]
            ))
        
        elif gap_type == "competency":
            # Recommend competency-specific learning
            recommendations.append(LearningRecommendation(
                recommendation_id=f"develop_{area}_{user_profile.user_id}",
                title=f"Develop {area.replace('_', ' ').title()} Competency",
                description=f"Strengthen your {area} skills through targeted learning activities",
                type="course",
                difficulty=user_profile.current_band,
                estimated_time=60,
                priority=priority,
                rationale=f"Your {area} competency score needs improvement",
                resources=self._get_competency_resources(area, user_profile.current_band),
                prerequisites=[]
            ))
        
        elif gap_type == "band_skill":
            # Recommend band-specific skill development
            recommendations.append(LearningRecommendation(
                recommendation_id=f"skill_{area}_{user_profile.user_id}",
                title=f"Master {area.replace('_', ' ').title()}",
                description=f"Develop essential {area} skills for Band {user_profile.current_band} level",
                type="scenario",
                difficulty=user_profile.current_band,
                estimated_time=45,
                priority=priority,
                rationale=f"{area} is a key skill required at your current band level",
                resources=self._get_skill_resources(area, user_profile.current_band),
                prerequisites=[]
            ))
        
        return recommendations

    def _create_progression_recommendations(self, user_profile: UserProfile) -> List[LearningRecommendation]:
        """Create recommendations for band progression"""
        recommendations = []
        
        current_band = user_profile.current_band
        band_info = self.band_progression_paths.get(current_band, {})
        
        if band_info.get("next_band"):
            next_band = band_info["next_band"]
            development_areas = band_info.get("development_areas", [])
            
            for area in development_areas:
                recommendations.append(LearningRecommendation(
                    recommendation_id=f"progression_{area}_{user_profile.user_id}",
                    title=f"Prepare for {next_band.replace('_', ' ').title()}: {area}",
                    description=f"Develop {area} skills to prepare for progression to {next_band}",
                    type="course",
                    difficulty=next_band,
                    estimated_time=90,
                    priority="medium",
                    rationale=f"Essential skill for progression to {next_band}",
                    resources=self._get_progression_resources(area, next_band),
                    prerequisites=[f"Current {current_band} competency"]
                ))
        
        return recommendations

    def _create_specialty_recommendations(self, user_profile: UserProfile) -> List[LearningRecommendation]:
        """Create specialty-specific recommendations"""
        recommendations = []
        
        specialty = user_profile.specialty
        band = user_profile.current_band
        
        # Get specialty-specific resources for current band
        band_key = f"band_{band.split('_')[1]}" if '_' in band else f"band_{band}"
        resources = self.learning_resources["specialty_specific"].get(specialty, [])
        
        for resource in resources[:3]:  # Limit to top 3 resources
            recommendations.append(LearningRecommendation(
                recommendation_id=f"specialty_{resource}_{user_profile.user_id}",
                title=f"{specialty.title()}: {resource}",
                description=f"Specialty-specific learning resource for {specialty} nursing",
                type="resource",
                difficulty=band,
                estimated_time=120,
                priority="low",
                rationale=f"Specialty-specific knowledge for {specialty} nursing",
                resources=[resource],
                prerequisites=[f"Basic {specialty} knowledge"]
            ))
        
        return recommendations

    def _prioritize_recommendations(self, recommendations: List[LearningRecommendation], 
                                  user_profile: UserProfile) -> List[LearningRecommendation]:
        """Prioritize recommendations based on user profile and preferences"""
        # Sort by priority and estimated time
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        def sort_key(rec):
            return (
                priority_order.get(rec.priority, 0),
                -rec.estimated_time,  # Longer activities first
                rec.title
            )
        
        return sorted(recommendations, key=sort_key, reverse=True)

    def _get_competency_resources(self, competency: str, band: str) -> List[str]:
        """Get resources for specific competency development"""
        competency_resources = {
            "Assessment": [
                "Clinical assessment skills course",
                "Patient assessment protocols",
                "Assessment documentation training"
            ],
            "Leadership": [
                "Leadership fundamentals course",
                "Team management training",
                "Conflict resolution workshop"
            ],
            "Communication": [
                "Therapeutic communication training",
                "Patient education skills",
                "Interprofessional communication"
            ],
            "Safety": [
                "Patient safety training",
                "Risk assessment course",
                "Incident reporting procedures"
            ]
        }
        
        return competency_resources.get(competency, ["General nursing development course"])

    def _get_skill_resources(self, skill: str, band: str) -> List[str]:
        """Get resources for specific skill development"""
        skill_resources = {
            "Basic clinical skills": [
                "Fundamental nursing skills course",
                "Clinical skills laboratory",
                "Mentorship program"
            ],
            "Leadership": [
                "Leadership development program",
                "Team leadership workshop",
                "Management fundamentals"
            ],
            "Quality improvement": [
                "Quality improvement methodology",
                "Audit and monitoring training",
                "Evidence-based practice course"
            ]
        }
        
        return skill_resources.get(skill, ["Professional development course"])

    def _get_progression_resources(self, area: str, next_band: str) -> List[str]:
        """Get resources for band progression"""
        progression_resources = {
            "Advanced clinical": [
                "Advanced clinical practice course",
                "Specialist clinical training",
                "Expert practice development"
            ],
            "Team leadership": [
                "Team leadership program",
                "Management and leadership course",
                "Advanced leadership skills"
            ],
            "Strategic thinking": [
                "Strategic planning course",
                "Healthcare strategy training",
                "Organizational development"
            ]
        }
        
        return progression_resources.get(area, ["Professional development course"])

    def create_learning_plan(self, user_profile: UserProfile, 
                           recommendations: List[LearningRecommendation]) -> Dict[str, Any]:
        """Create a structured learning plan from recommendations"""
        
        # Group recommendations by type
        plan_by_type = {}
        for rec in recommendations:
            if rec.type not in plan_by_type:
                plan_by_type[rec.type] = []
            plan_by_type[rec.type].append(rec)
        
        # Create weekly schedule based on available time
        weekly_plan = self._create_weekly_schedule(user_profile, recommendations)
        
        return {
            "user_id": user_profile.user_id,
            "current_band": user_profile.current_band,
            "specialty": user_profile.specialty,
            "total_recommendations": len(recommendations),
            "estimated_total_time": sum(rec.estimated_time for rec in recommendations),
            "plan_by_type": plan_by_type,
            "weekly_schedule": weekly_plan,
            "created_date": datetime.now().isoformat(),
            "review_date": (datetime.now() + timedelta(weeks=4)).isoformat()
        }

    def _create_weekly_schedule(self, user_profile: UserProfile, 
                              recommendations: List[LearningRecommendation]) -> List[Dict[str, Any]]:
        """Create a weekly learning schedule"""
        weekly_time = user_profile.time_available
        schedule = []
        
        # Sort recommendations by priority and time
        sorted_recs = sorted(recommendations, key=lambda x: (
            {"high": 3, "medium": 2, "low": 1}[x.priority],
            -x.estimated_time
        ), reverse=True)
        
        current_week = 1
        current_week_time = 0
        week_activities = []
        
        for rec in sorted_recs:
            if current_week_time + rec.estimated_time <= weekly_time:
                week_activities.append({
                    "recommendation_id": rec.recommendation_id,
                    "title": rec.title,
                    "type": rec.type,
                    "estimated_time": rec.estimated_time,
                    "priority": rec.priority
                })
                current_week_time += rec.estimated_time
            else:
                # Start new week
                if week_activities:
                    schedule.append({
                        "week": current_week,
                        "activities": week_activities,
                        "total_time": current_week_time
                    })
                
                current_week += 1
                current_week_time = rec.estimated_time
                week_activities = [{
                    "recommendation_id": rec.recommendation_id,
                    "title": rec.title,
                    "type": rec.type,
                    "estimated_time": rec.estimated_time,
                    "priority": rec.priority
                }]
        
        # Add final week
        if week_activities:
            schedule.append({
                "week": current_week,
                "activities": week_activities,
                "total_time": current_week_time
            })
        
        return schedule

def main():
    """Example usage of the PersonalizedRecommendationService"""
    service = PersonalizedRecommendationService()
    
    # Example user profile
    user_profile = UserProfile(
        user_id="user_123",
        current_band="band_5",
        specialty="icu",
        experience_level="intermediate",
        strengths=["Assessment", "Patient care", "Communication"],
        weaknesses=["Leadership", "Quality improvement"],
        learning_goals=["Progress to Band 6", "Develop leadership skills"],
        preferred_learning_style="practical",
        time_available=180,  # 3 hours per week
        last_activity=datetime.now()
    )
    
    # Example performance data
    performance_data = {
        "question_performance": {
            "scenario": {"accuracy": 0.6},
            "calculation": {"accuracy": 0.8},
            "multiple_choice": {"accuracy": 0.9}
        },
        "competency_performance": {
            "Leadership": {"score": 2},
            "Quality improvement": {"score": 1},
            "Assessment": {"score": 4}
        }
    }
    
    # Generate recommendations
    recommendations = service.generate_personalized_recommendations(user_profile, performance_data)
    
    # Create learning plan
    learning_plan = service.create_learning_plan(user_profile, recommendations)
    
    print(f"Generated {len(recommendations)} personalized recommendations")
    print(f"Learning plan created with {len(learning_plan['weekly_schedule'])} weeks of activities")

if __name__ == "__main__":
    main()
