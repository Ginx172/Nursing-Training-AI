#!/usr/bin/env python3
"""
Enhanced Question Generator for NHS Nursing Bands
Adapts questions based on band level and specialty requirements
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime

class EnhancedQuestionGenerator:
    def __init__(self):
        self.band_competencies = {
            "band_2": {
                "level": "Foundation",
                "focus": ["Basic clinical skills", "Patient safety", "Communication", "Teamwork"],
                "leadership": "None",
                "management": "None",
                "governance": "None"
            },
            "band_3": {
                "level": "Foundation+",
                "focus": ["Clinical skills", "Patient care", "Basic supervision", "Learning"],
                "leadership": "Minimal",
                "management": "None",
                "governance": "None"
            },
            "band_4": {
                "level": "Intermediate",
                "focus": ["Clinical expertise", "Basic leadership", "Mentoring", "Quality improvement"],
                "leadership": "Basic",
                "management": "Minimal",
                "governance": "Basic"
            },
            "band_5": {
                "level": "Staff Nurse",
                "focus": ["Clinical expertise", "Leadership", "Mentoring", "Quality improvement", "Teaching"],
                "leadership": "Moderate",
                "management": "Basic",
                "governance": "Moderate"
            },
            "band_6": {
                "level": "Senior Staff Nurse",
                "focus": ["Advanced clinical", "Team leadership", "Management", "Governance", "Audit"],
                "leadership": "Advanced",
                "management": "Moderate",
                "governance": "Advanced"
            },
            "band_7": {
                "level": "Charge Nurse/Sister",
                "focus": ["Strategic leadership", "Service management", "Policy development", "Advanced governance"],
                "leadership": "Strategic",
                "management": "Advanced",
                "governance": "Strategic"
            },
            "band_8": {
                "level": "Matron/Manager",
                "focus": ["Strategic management", "Service development", "Policy implementation", "Organizational leadership"],
                "leadership": "Executive",
                "management": "Strategic",
                "governance": "Executive"
            },
            "band_9": {
                "level": "Director/Executive",
                "focus": ["Executive leadership", "Strategic planning", "Organizational development", "Policy creation"],
                "leadership": "Executive",
                "management": "Executive",
                "governance": "Executive"
            }
        }
        
        self.question_types = {
            "multiple_choice": {
                "band_2_3": "Basic clinical knowledge, safety protocols",
                "band_4_5": "Clinical reasoning, basic leadership",
                "band_6_7": "Advanced clinical, management principles",
                "band_8_9": "Strategic thinking, policy knowledge"
            },
            "scenario": {
                "band_2_3": "Basic patient care scenarios",
                "band_4_5": "Complex patient care, team situations",
                "band_6_7": "Leadership challenges, management scenarios",
                "band_8_9": "Strategic decisions, organizational challenges"
            },
            "calculation": {
                "band_2_3": "Basic drug calculations, vital signs",
                "band_4_5": "Complex drug calculations, fluid balance",
                "band_6_7": "Advanced calculations, resource management",
                "band_8_9": "Budget calculations, performance metrics"
            },
            "case_study": {
                "band_2_3": "Simple patient cases",
                "band_4_5": "Complex patient cases with multiple factors",
                "band_6_7": "Service improvement cases",
                "band_8_9": "Organizational change cases"
            },
            "leadership": {
                "band_2_3": "None",
                "band_4_5": "Basic team leadership",
                "band_6_7": "Advanced team leadership, conflict resolution",
                "band_8_9": "Strategic leadership, organizational change"
            },
            "governance": {
                "band_2_3": "Basic safety, reporting",
                "band_4_5": "Quality improvement, audit basics",
                "band_6_7": "Advanced audit, policy implementation",
                "band_8_9": "Strategic governance, policy development"
            }
        }

    def generate_band_specific_questions(self, specialty: str, band: str, num_questions: int = 50) -> List[Dict]:
        """Generate questions adapted to specific band level"""
        band_key = f"band_{band}"
        if band_key not in self.band_competencies:
            raise ValueError(f"Invalid band: {band}")
        
        questions = []
        band_info = self.band_competencies[band_key]
        
        # Determine question distribution based on band level
        if band in ["2", "3"]:
            question_distribution = {
                "multiple_choice": 0.4,
                "scenario": 0.3,
                "calculation": 0.2,
                "case_study": 0.1
            }
        elif band in ["4", "5"]:
            question_distribution = {
                "multiple_choice": 0.3,
                "scenario": 0.3,
                "calculation": 0.2,
                "case_study": 0.15,
                "leadership": 0.05
            }
        elif band in ["6", "7"]:
            question_distribution = {
                "multiple_choice": 0.2,
                "scenario": 0.25,
                "calculation": 0.15,
                "case_study": 0.2,
                "leadership": 0.15,
                "governance": 0.05
            }
        else:  # Band 8-9
            question_distribution = {
                "multiple_choice": 0.15,
                "scenario": 0.2,
                "calculation": 0.1,
                "case_study": 0.25,
                "leadership": 0.2,
                "governance": 0.1
            }
        
        # Generate questions based on distribution
        question_id = 1
        for question_type, percentage in question_distribution.items():
            num_type_questions = int(num_questions * percentage)
            for i in range(num_type_questions):
                question = self._create_question(
                    specialty=specialty,
                    band=band,
                    question_type=question_type,
                    question_id=question_id,
                    band_info=band_info
                )
                questions.append(question)
                question_id += 1
        
        return questions

    def _create_question(self, specialty: str, band: str, question_type: str, question_id: int, band_info: Dict) -> Dict:
        """Create a specific question based on type and band level"""
        
        base_question = {
            "id": question_id,
            "specialty": specialty,
            "band": f"band_{band}",
            "question_type": question_type,
            "difficulty": self._get_difficulty_level(band),
            "competencies": self._get_competencies(specialty, band, question_type),
            "expected_points": self._get_expected_points(specialty, band, question_type),
            "references": self._get_references(specialty, band),
            "learning_outcomes": self._get_learning_outcomes(specialty, band, question_type),
            "created_date": datetime.now().isoformat(),
            "version": "2.0"
        }
        
        # Add type-specific content
        if question_type == "multiple_choice":
            base_question.update(self._create_multiple_choice_question(specialty, band))
        elif question_type == "scenario":
            base_question.update(self._create_scenario_question(specialty, band))
        elif question_type == "calculation":
            base_question.update(self._create_calculation_question(specialty, band))
        elif question_type == "case_study":
            base_question.update(self._create_case_study_question(specialty, band))
        elif question_type == "leadership":
            base_question.update(self._create_leadership_question(specialty, band))
        elif question_type == "governance":
            base_question.update(self._create_governance_question(specialty, band))
        
        return base_question

    def _get_difficulty_level(self, band: str) -> str:
        """Get difficulty level based on band"""
        difficulty_map = {
            "2": "beginner",
            "3": "beginner",
            "4": "intermediate",
            "5": "intermediate",
            "6": "advanced",
            "7": "advanced",
            "8": "expert",
            "9": "expert"
        }
        return difficulty_map.get(band, "intermediate")

    def _get_competencies(self, specialty: str, band: str, question_type: str) -> List[str]:
        """Get competencies based on specialty, band, and question type"""
        base_competencies = {
            "amu": ["Assessment", "Patient care", "Safety", "Communication", "Acute care"],
            "cardiology": ["Cardiac assessment", "ECG interpretation", "Medication management", "Patient education"],
            "emergency": ["Triage", "Emergency care", "Trauma management", "Rapid assessment"],
            "icu": ["Critical care", "Ventilator management", "Hemodynamic monitoring", "Family support"],
            "maternity": ["Antenatal care", "Labour management", "Postnatal care", "Newborn care"],
            "mental_health": ["Mental health assessment", "Crisis intervention", "Therapeutic communication", "Risk assessment"],
            "neurology": ["Neurological assessment", "Seizure management", "Stroke care", "Rehabilitation"],
            "oncology": ["Cancer care", "Chemotherapy management", "Palliative care", "Family support"],
            "pediatrics": ["Pediatric assessment", "Growth monitoring", "Family-centered care", "Child development"]
        }
        
        competencies = base_competencies.get(specialty, ["Assessment", "Patient care", "Safety"])
        
        # Add band-specific competencies
        if int(band) >= 4:
            competencies.extend(["Leadership", "Mentoring", "Quality improvement"])
        if int(band) >= 6:
            competencies.extend(["Team management", "Governance", "Audit"])
        if int(band) >= 8:
            competencies.extend(["Strategic planning", "Policy development", "Organizational leadership"])
        
        return competencies

    def _get_expected_points(self, specialty: str, band: str, question_type: str) -> List[str]:
        """Get expected points based on specialty, band, and question type"""
        points = []
        
        if question_type == "multiple_choice":
            points = [
                "Demonstrate knowledge of clinical guidelines",
                "Apply evidence-based practice",
                "Show understanding of safety protocols"
            ]
        elif question_type == "scenario":
            points = [
                "Assess patient condition appropriately",
                "Implement evidence-based interventions",
                "Communicate effectively with team",
                "Document care accurately"
            ]
        elif question_type == "calculation":
            points = [
                "Perform accurate calculations",
                "Verify calculations independently",
                "Apply safety checks"
            ]
        elif question_type == "case_study":
            points = [
                "Analyze complex patient situations",
                "Develop comprehensive care plans",
                "Consider multiple factors",
                "Evaluate outcomes"
            ]
        elif question_type == "leadership":
            points = [
                "Demonstrate leadership skills",
                "Manage team dynamics",
                "Resolve conflicts effectively",
                "Support staff development"
            ]
        elif question_type == "governance":
            points = [
                "Understand governance principles",
                "Implement quality improvements",
                "Conduct audits effectively",
                "Develop policies"
            ]
        
        # Add band-specific points
        if int(band) >= 6:
            points.extend(["Show advanced clinical reasoning", "Demonstrate management skills"])
        if int(band) >= 8:
            points.extend(["Exhibit strategic thinking", "Lead organizational change"])
        
        return points

    def _get_references(self, specialty: str, band: str) -> List[str]:
        """Get relevant references based on specialty and band"""
        references = [
            "NMC Code of Professional Practice",
            "NICE Guidelines",
            "Evidence-based practice guidelines"
        ]
        
        specialty_refs = {
            "amu": ["NICE CG127 - Hypertension Management", "NICE NG51 - Sepsis Recognition"],
            "cardiology": ["NICE CG181 - Chest Pain", "NICE CG95 - Heart Failure"],
            "emergency": ["NICE CG176 - Head Injury Assessment", "NICE NG39 - Major Trauma"],
            "icu": ["NICE CG50 - Recognition and Response to Acute Illness", "NICE NG74 - Critical Care"],
            "maternity": ["NICE CG190 - Intrapartum Care", "NICE CG62 - Antenatal Care"],
            "mental_health": ["NICE NG10 - Violence and Aggression Management", "NICE CG178 - Depression"],
            "neurology": ["NICE CG68 - Stroke", "NICE CG137 - Epilepsy"],
            "oncology": ["NICE CG81 - Cancer Services", "NICE CG142 - Cancer of Unknown Primary"],
            "pediatrics": ["NICE CG160 - Fever in Under 5s", "NICE CG76 - Diarrhoea and Vomiting"]
        }
        
        references.extend(specialty_refs.get(specialty, []))
        return references

    def _get_learning_outcomes(self, specialty: str, band: str, question_type: str) -> List[str]:
        """Get learning outcomes based on specialty, band, and question type"""
        outcomes = [
            f"Demonstrate competency in {specialty} nursing at Band {band} level",
            "Apply evidence-based practice principles",
            "Maintain patient safety standards"
        ]
        
        if int(band) >= 4:
            outcomes.append("Show leadership and mentoring capabilities")
        if int(band) >= 6:
            outcomes.append("Demonstrate management and governance skills")
        if int(band) >= 8:
            outcomes.append("Exhibit strategic leadership and organizational development")
        
        return outcomes

    def _create_multiple_choice_question(self, specialty: str, band: str) -> Dict:
        """Create multiple choice question content"""
        return {
            "title": f"Clinical Knowledge - {specialty.title()} Band {band}",
            "question_text": f"What is the most appropriate action when managing a patient with [condition] in {specialty}?",
            "options": [
                "Option A - Basic intervention",
                "Option B - Evidence-based intervention", 
                "Option C - Advanced intervention",
                "Option D - Specialist intervention"
            ],
            "correct_answer": "Option B - Evidence-based intervention",
            "explanation": f"This question tests your knowledge of evidence-based practice in {specialty} nursing at Band {band} level.",
            "rationale": "Evidence-based practice ensures the best patient outcomes and is fundamental to professional nursing practice."
        }

    def _create_scenario_question(self, specialty: str, band: str) -> Dict:
        """Create scenario question content"""
        return {
            "title": f"Clinical Scenario - {specialty.title()} Band {band}",
            "question_text": f"Describe your approach to managing a complex patient situation in {specialty} where [specific scenario details].",
            "scenario_details": {
                "patient_age": "Variable based on specialty",
                "presenting_condition": "Specialty-specific condition",
                "complications": "Multiple factors to consider",
                "environment": f"{specialty} department setting"
            },
            "expected_response": f"Demonstrate systematic assessment, evidence-based interventions, and effective communication in {specialty} nursing.",
            "marking_criteria": [
                "Accurate assessment (25%)",
                "Appropriate interventions (25%)",
                "Effective communication (25%)",
                "Safety considerations (25%)"
            ]
        }

    def _create_calculation_question(self, specialty: str, band: str) -> Dict:
        """Create calculation question content"""
        return {
            "title": f"Clinical Calculation - {specialty.title()} Band {band}",
            "question_text": f"Calculate the correct dosage for [medication] for a patient in {specialty} with the following parameters: [specific values]",
            "calculation_type": "Drug dosage calculation",
            "given_values": {
                "patient_weight": "Variable",
                "medication_concentration": "Variable",
                "prescribed_dose": "Variable"
            },
            "formula": "Dose = (Prescribed dose × Patient weight) / Concentration",
            "safety_checks": [
                "Verify calculation independently",
                "Check against normal dose ranges",
                "Confirm with senior colleague if uncertain"
            ],
            "expected_answer": "Calculated dosage with units",
            "tolerance": "±5%"
        }

    def _create_case_study_question(self, specialty: str, band: str) -> Dict:
        """Create case study question content"""
        return {
            "title": f"Case Study - {specialty.title()} Band {band}",
            "question_text": f"Analyze this complex case in {specialty} and develop a comprehensive care plan.",
            "case_study": {
                "patient_history": "Detailed patient background",
                "presenting_condition": "Current health status",
                "social_factors": "Family, support systems",
                "psychological_factors": "Mental health considerations",
                "environmental_factors": "Living situation, resources"
            },
            "analysis_requirements": [
                "Identify key issues",
                "Prioritize care needs",
                "Develop interventions",
                "Consider outcomes"
            ],
            "care_plan_components": [
                "Assessment findings",
                "Nursing diagnoses",
                "Goals and outcomes",
                "Interventions",
                "Evaluation criteria"
            ]
        }

    def _create_leadership_question(self, specialty: str, band: str) -> Dict:
        """Create leadership question content"""
        return {
            "title": f"Leadership Challenge - {specialty.title()} Band {band}",
            "question_text": f"Describe how you would lead your team through [specific leadership challenge] in {specialty}.",
            "leadership_scenario": {
                "situation": "Team conflict, change management, or crisis",
                "stakeholders": "Team members, patients, families, management",
                "constraints": "Time, resources, policies",
                "desired_outcome": "Improved team performance, patient care"
            },
            "leadership_competencies": [
                "Communication",
                "Conflict resolution",
                "Team building",
                "Change management",
                "Decision making"
            ],
            "expected_approach": f"Demonstrate Band {band} level leadership skills appropriate for {specialty} nursing."
        }

    def _create_governance_question(self, specialty: str, band: str) -> Dict:
        """Create governance question content"""
        return {
            "title": f"Governance and Quality - {specialty.title()} Band {band}",
            "question_text": f"How would you implement a quality improvement initiative in {specialty} to address [specific issue]?",
            "governance_scenario": {
                "issue": "Quality or safety concern",
                "current_state": "Baseline performance",
                "target_state": "Desired improvement",
                "stakeholders": "Staff, patients, management, regulators"
            },
            "governance_components": [
                "Audit and monitoring",
                "Policy development",
                "Staff education",
                "Performance measurement",
                "Continuous improvement"
            ],
            "implementation_plan": [
                "Assessment phase",
                "Planning phase", 
                "Implementation phase",
                "Evaluation phase"
            ]
        }

    def generate_enhanced_question_bank(self, specialty: str, band: str, num_questions: int = 50) -> Dict:
        """Generate complete enhanced question bank for specialty and band"""
        questions = self.generate_band_specific_questions(specialty, band, num_questions)
        
        # Calculate statistics
        question_types = {}
        for q in questions:
            q_type = q["question_type"]
            question_types[q_type] = question_types.get(q_type, 0) + 1
        
        return {
            "band": f"band_{band}",
            "specialty": specialty,
            "bank_id": f"{specialty}_band_{band}_enhanced",
            "version": "2.0",
            "total_questions": len(questions),
            "question_type_distribution": question_types,
            "difficulty_level": self._get_difficulty_level(band),
            "competencies_covered": list(set([comp for q in questions for comp in q["competencies"]])),
            "created_date": datetime.now().isoformat(),
            "enhancement_features": [
                "Band-specific difficulty levels",
                "Comprehensive competencies mapping",
                "Evidence-based references",
                "Detailed learning outcomes",
                "Progressive skill development",
                "NICE guidelines integration"
            ],
            "questions": questions
        }

def main():
    """Main function to generate enhanced question banks"""
    generator = EnhancedQuestionGenerator()
    
    specialties = ["amu", "cardiology", "emergency", "icu", "maternity", "mental_health", "neurology", "oncology", "pediatrics"]
    bands = ["2", "3", "4", "5", "6", "7", "8", "9"]
    
    output_dir = "Nursing_Training_AI_App/backend/data/enhanced_question_banks"
    os.makedirs(output_dir, exist_ok=True)
    
    for specialty in specialties:
        for band in bands:
            print(f"Generating enhanced questions for {specialty} Band {band}...")
            
            question_bank = generator.generate_enhanced_question_bank(specialty, band, 50)
            
            filename = f"{specialty}_band_{band}_enhanced.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(question_bank, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Created {filename} with {question_bank['total_questions']} questions")

if __name__ == "__main__":
    main()
