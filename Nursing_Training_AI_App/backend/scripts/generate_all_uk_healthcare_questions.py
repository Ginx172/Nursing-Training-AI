#!/usr/bin/env python3
"""
Complete UK Healthcare Question Generator
Generates questions for ALL UK healthcare sectors with proper band structure
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime

class UKHealthcareQuestionGenerator:
    def __init__(self):
        # Correct NHS Band structure (NO Band 9)
        self.bands = {
            "band_2": {"min_questions": 10, "max_questions": 12, "level": "Foundation"},
            "band_3": {"min_questions": 12, "max_questions": 15, "level": "Foundation+"},
            "band_4": {"min_questions": 14, "max_questions": 18, "level": "Intermediate"},
            "band_5": {"min_questions": 16, "max_questions": 21, "level": "Registered Nurse"},
            "band_6": {"min_questions": 18, "max_questions": 24, "level": "Senior Nurse"},
            "band_7": {"min_questions": 20, "max_questions": 27, "level": "Advanced Practitioner"},
            "band_8a": {"min_questions": 22, "max_questions": 30, "level": "Senior Manager"},
            "band_8b": {"min_questions": 24, "max_questions": 33, "level": "Associate Director"},
            "band_8c": {"min_questions": 26, "max_questions": 36, "level": "Director"},
            "band_8d": {"min_questions": 28, "max_questions": 39, "level": "Executive Director"}
        }
        
        self.sectors = {
            "nhs": {
                "name": "NHS Hospitals",
                "specialties": ["amu", "emergency", "icu", "maternity", "mental_health", 
                               "pediatrics", "cardiology", "neurology", "oncology"],
                "applicable_bands": ["band_2", "band_3", "band_4", "band_5", "band_6", "band_7", 
                                    "band_8a", "band_8b", "band_8c", "band_8d"]
            },
            "private_healthcare": {
                "name": "Private Healthcare",
                "specialties": ["theatre", "recovery", "ward", "endoscopy", "cosmetic", "pre_assessment"],
                "applicable_bands": ["band_2", "band_3", "band_4", "band_5", "band_6", "band_7"]
            },
            "care_homes": {
                "name": "Care Homes & Residential Care",
                "specialties": ["residential_care", "nursing_home", "dementia_care", "palliative_care"],
                "applicable_bands": ["band_2", "band_3", "band_4", "band_5", "band_6", "band_7", "band_8a"]
            },
            "community": {
                "name": "Community Healthcare",
                "specialties": ["district_nursing", "health_visiting", "community_mental_health", 
                               "school_nursing", "community_matron"],
                "applicable_bands": ["band_4", "band_5", "band_6", "band_7", "band_8a"]
            },
            "primary_care": {
                "name": "Primary Care / GP Surgeries",
                "specialties": ["practice_nursing", "advanced_practitioner", "hca_primary_care", 
                               "chronic_disease", "immunizations"],
                "applicable_bands": ["band_2", "band_3", "band_4", "band_5", "band_6", "band_7", "band_8a"]
            }
        }

        # Minimum 10 banks per sector
        self.min_banks_per_sector = 10

    def get_question_count(self, band: str, bank_number: int) -> int:
        """Calculate number of questions for a specific band and bank"""
        band_info = self.bands[band]
        min_q = band_info["min_questions"]
        max_q = band_info["max_questions"]
        
        # Vary within range based on bank number
        variation = (bank_number % 3)  # 0, 1, or 2
        if max_q - min_q <= 2:
            return min_q + variation
        else:
            return min_q + (variation * ((max_q - min_q) // 2))

    def generate_sector_questions(self, sector: str, specialty: str, band: str, 
                                 bank_number: int) -> Dict[str, Any]:
        """Generate questions for specific sector, specialty, and band"""
        
        num_questions = self.get_question_count(band, bank_number)
        sector_info = self.sectors[sector]
        band_info = self.bands[band]
        
        questions = []
        
        # Question type distribution based on band level
        if band in ["band_2", "band_3"]:
            distribution = {
                "multiple_choice": 0.5,
                "scenario": 0.3,
                "calculation": 0.2
            }
        elif band in ["band_4", "band_5"]:
            distribution = {
                "multiple_choice": 0.3,
                "scenario": 0.4,
                "calculation": 0.2,
                "case_study": 0.1
            }
        elif band in ["band_6", "band_7"]:
            distribution = {
                "multiple_choice": 0.2,
                "scenario": 0.3,
                "case_study": 0.2,
                "leadership": 0.2,
                "governance": 0.1
            }
        else:  # Band 8a, 8b, 8c, 8d
            distribution = {
                "multiple_choice": 0.1,
                "scenario": 0.2,
                "case_study": 0.3,
                "leadership": 0.25,
                "governance": 0.15
            }
        
        question_id = 1
        for q_type, percentage in distribution.items():
            num_of_type = int(num_questions * percentage)
            for _ in range(num_of_type):
                question = self._create_sector_specific_question(
                    sector, specialty, band, q_type, question_id
                )
                questions.append(question)
                question_id += 1
        
        # Fill remaining questions if needed
        while len(questions) < num_questions:
            question = self._create_sector_specific_question(
                sector, specialty, band, "multiple_choice", question_id
            )
            questions.append(question)
            question_id += 1
        
        return {
            "sector": sector,
            "sector_name": sector_info["name"],
            "specialty": specialty,
            "band": band,
            "band_level": band_info["level"],
            "bank_number": bank_number,
            "bank_id": f"{sector}_{specialty}_{band}_bank_{bank_number:02d}",
            "version": "1.0",
            "total_questions": len(questions),
            "created_date": datetime.now().isoformat(),
            "questions": questions
        }

    def _create_sector_specific_question(self, sector: str, specialty: str, 
                                        band: str, q_type: str, q_id: int) -> Dict[str, Any]:
        """Create sector-specific question"""
        
        base_question = {
            "id": q_id,
            "sector": sector,
            "specialty": specialty,
            "band": band,
            "question_type": q_type,
            "created_date": datetime.now().isoformat()
        }
        
        # Add sector-specific content
        if sector == "private_healthcare":
            base_question.update(self._private_healthcare_question(specialty, band, q_type))
        elif sector == "care_homes":
            base_question.update(self._care_home_question(specialty, band, q_type))
        elif sector == "community":
            base_question.update(self._community_question(specialty, band, q_type))
        elif sector == "primary_care":
            base_question.update(self._primary_care_question(specialty, band, q_type))
        else:  # NHS - use existing structure
            base_question.update(self._nhs_question(specialty, band, q_type))
        
        return base_question

    def _private_healthcare_question(self, specialty: str, band: str, q_type: str) -> Dict:
        """Private healthcare specific questions"""
        if q_type == "multiple_choice":
            return {
                "title": f"Private Healthcare - {specialty.replace('_', ' ').title()}",
                "question_text": f"A private patient is dissatisfied with their post-operative care. What is the MOST appropriate response?",
                "options": [
                    "A) Apologize and escalate to consultant immediately",
                    "B) Listen to concerns, document, and follow private hospital complaints procedure",
                    "C) Explain that standards are same as NHS",
                    "D) Refer to hospital manager"
                ],
                "correct_answer": "B) Listen to concerns, document, and follow private hospital complaints procedure",
                "explanation": "Private healthcare requires excellent customer service while following proper procedures",
                "competencies": ["Customer service", "Communication", "Complaints management", "Patient satisfaction"],
                "sector_specific": ["Private insurance knowledge", "Patient expectations management"]
            }
        elif q_type == "scenario":
            return {
                "title": f"Private Healthcare Scenario - {specialty.replace('_', ' ').title()}",
                "question_text": f"A private patient's insurance company declines coverage for their procedure. How do you handle this situation?",
                "expected_response": "Explain situation sensitively, provide written breakdown of costs, discuss self-pay options, refer to finance team, maintain professional relationship",
                "competencies": ["Communication", "Financial awareness", "Patient advocacy", "Problem-solving"],
                "sector_specific": ["Insurance knowledge", "Self-pay procedures", "Financial counseling"]
            }
        elif q_type == "case_study":
            return {
                "title": f"Private Healthcare Case Study - {specialty.replace('_', ' ').title()}",
                "question_text": "Manage a VIP patient with high expectations undergoing elective surgery",
                "case_details": {
                    "patient_type": "High-net-worth individual",
                    "expectations": "Extremely high",
                    "challenges": "Demanding family, media interest, special requirements"
                },
                "competencies": ["VIP patient management", "Discretion", "Excellence in care", "Media awareness"]
            }
        else:
            return {
                "title": f"Private Healthcare - {q_type.replace('_', ' ').title()}",
                "question_text": f"Question about {specialty} in private healthcare context",
                "competencies": ["Clinical excellence", "Customer service", "Private sector knowledge"]
            }

    def _care_home_question(self, specialty: str, band: str, q_type: str) -> Dict:
        """Care home specific questions"""
        if q_type == "multiple_choice":
            return {
                "title": f"Care Home - {specialty.replace('_', ' ').title()}",
                "question_text": "A resident with dementia is refusing medication. What is the BEST approach?",
                "options": [
                    "A) Administer covertly in food without assessment",
                    "B) Assess capacity, document, involve family, consider best interests",
                    "C) Call GP immediately for forcible administration order",
                    "D) Record as refused and take no further action"
                ],
                "correct_answer": "B) Assess capacity, document, involve family, consider best interests",
                "explanation": "Must follow Mental Capacity Act 2005 principles",
                "competencies": ["Mental Capacity Act", "Dementia care", "Medication management", "Best interests"],
                "sector_specific": ["CQC standards", "DoLS knowledge", "Safeguarding"]
            }
        elif q_type == "scenario":
            return {
                "title": f"Care Home Scenario - {specialty.replace('_', ' ').title()}",
                "question_text": "A resident is approaching end of life. Family are in disagreement about care plan. How do you manage this?",
                "expected_response": "Hold family meeting, explain resident's wishes if known, discuss advance care planning, involve GP/palliative team, document decisions, ensure dignity maintained",
                "competencies": ["End of life care", "Family communication", "Conflict resolution", "Advance care planning"],
                "sector_specific": ["ReSPECT forms", "Palliative care protocols", "Bereavement support"]
            }
        elif q_type == "governance":
            return {
                "title": f"Care Home Governance - {specialty.replace('_', ' ').title()}",
                "question_text": "CQC inspection is announced for next week. What are your priorities as {band.replace('_', ' ')}?",
                "expected_response": "Review care plans, medication audits, staff training records, safeguarding documentation, accident/incident logs, ensure environment safe, brief staff, check policies updated",
                "competencies": ["CQC standards", "Quality assurance", "Compliance", "Leadership"],
                "sector_specific": ["CQC key lines of enquiry", "Safe/Effective/Caring/Responsive/Well-led"]
            }
        else:
            return {
                "title": f"Care Home - {q_type.replace('_', ' ').title()}",
                "question_text": f"Question about {specialty} in care home setting",
                "competencies": ["Long-term care", "Person-centered care", "CQC compliance"]
            }

    def _community_question(self, specialty: str, band: str, q_type: str) -> Dict:
        """Community healthcare specific questions"""
        if q_type == "multiple_choice":
            return {
                "title": f"Community - {specialty.replace('_', ' ').title()}",
                "question_text": "During a home visit, you notice signs of potential abuse. What is your IMMEDIATE action?",
                "options": [
                    "A) Confront the family member immediately",
                    "B) Complete visit, document concerns, follow safeguarding procedure, contact safeguarding lead",
                    "C) Call police immediately from the home",
                    "D) Leave and discuss with manager next day"
                ],
                "correct_answer": "B) Complete visit, document concerns, follow safeguarding procedure, contact safeguarding lead",
                "explanation": "Safeguarding is priority but must follow procedure and ensure own safety",
                "competencies": ["Safeguarding adults", "Professional judgment", "Documentation", "Multi-agency working"],
                "sector_specific": ["Lone working safety", "Safeguarding referral process"]
            }
        elif q_type == "scenario":
            return {
                "title": f"Community Scenario - {specialty.replace('_', ' ').title()}",
                "question_text": "You have 8 home visits scheduled but receive urgent referral for palliative patient. How do you manage your caseload?",
                "expected_response": "Assess urgency of all visits, reprioritize, contact patients to reschedule non-urgent, arrange colleague support if needed, ensure palliative patient seen same day, document decisions",
                "competencies": ["Caseload management", "Prioritization", "Communication", "Time management", "Clinical judgment"],
                "sector_specific": ["Autonomous decision-making", "Lone working", "Resource management"]
            }
        elif q_type == "leadership":
            return {
                "title": f"Community Leadership - {specialty.replace('_', ' ').title()}",
                "question_text": "As {band.replace('_', ' ')}, how do you support a newly qualified community nurse struggling with lone working?",
                "expected_response": "Regular supervision, joint visits, debrief sessions, assess confidence levels, gradual independence, peer support, access to senior advice, safety procedures",
                "competencies": ["Mentoring", "Clinical supervision", "Leadership", "Staff development"],
                "sector_specific": ["Lone working support", "Community nursing competencies"]
            }
        else:
            return {
                "title": f"Community - {q_type.replace('_', ' ').title()}",
                "question_text": f"Question about {specialty} in community setting",
                "competencies": ["Autonomous practice", "Home visiting", "Multi-agency working"]
            }

    def _primary_care_question(self, specialty: str, band: str, q_type: str) -> Dict:
        """Primary care specific questions"""
        if q_type == "multiple_choice":
            return {
                "title": f"Primary Care - {specialty.replace('_', ' ').title()}",
                "question_text": "A patient attends asthma review with peak flow below target. What is your NEXT step?",
                "options": [
                    "A) Immediately increase inhaled steroid dose",
                    "B) Assess technique, adherence, triggers, consider step up if indicated per BTS guidelines",
                    "C) Refer to respiratory consultant",
                    "D) Tell patient to see GP"
                ],
                "correct_answer": "B) Assess technique, adherence, triggers, consider step up if indicated per BTS guidelines",
                "explanation": "Follow systematic assessment before escalating treatment",
                "competencies": ["Chronic disease management", "Clinical assessment", "Protocol-driven care", "Patient education"],
                "sector_specific": ["BTS/SIGN guidelines", "QOF indicators", "Asthma management"]
            }
        elif q_type == "scenario":
            return {
                "title": f"Primary Care Scenario - {specialty.replace('_', ' ').title()}",
                "question_text": "Running 30 minutes behind in clinic with 5 patients still waiting. How do you manage?",
                "expected_response": "Apologize to waiting patients, give realistic wait time, offer rebooking, ensure each patient gets quality time not rushed care, identify why running late, discuss with manager if systemic issue",
                "competencies": ["Time management", "Communication", "Patient-centered care", "Problem-solving"],
                "sector_specific": ["Appointment management", "Patient satisfaction", "Clinic efficiency"]
            }
        elif q_type == "calculation":
            return {
                "title": f"Primary Care Calculation - {specialty.replace('_', ' ').title()}",
                "question_text": "Calculate correct child immunization dosage for 2-month-old baby weighing 5.2kg",
                "calculation_type": "Pediatric immunization dosage",
                "competencies": ["Immunization knowledge", "Safe practice", "Calculation accuracy"],
                "sector_specific": ["Green Book guidelines", "Immunization schedule"]
            }
        else:
            return {
                "title": f"Primary Care - {q_type.replace('_', ' ').title()}",
                "question_text": f"Question about {specialty} in GP surgery",
                "competencies": ["Primary care nursing", "Chronic disease management", "Prevention"]
            }

    def _nhs_question(self, specialty: str, band: str, q_type: str) -> Dict:
        """NHS hospital questions - use existing structure"""
        return {
            "title": f"NHS {specialty.replace('_', ' ').title()} - {band.replace('_', ' ').title()}",
            "question_text": f"Clinical question for {specialty} at {band} level",
            "competencies": ["Clinical expertise", "Patient safety", "Evidence-based practice"],
            "sector_specific": ["NHS values", "NICE guidelines"]
        }

    def generate_all_questions(self):
        """Generate questions for all sectors, specialties, and bands"""
        output_base = "Nursing_Training_AI_App/backend/data/uk_healthcare_questions"
        os.makedirs(output_base, exist_ok=True)
        
        total_banks = 0
        
        for sector, sector_info in self.sectors.items():
            print(f"\n{'='*60}")
            print(f"Generating questions for: {sector_info['name']}")
            print(f"{'='*60}")
            
            sector_dir = os.path.join(output_base, sector)
            os.makedirs(sector_dir, exist_ok=True)
            
            for specialty in sector_info["specialties"]:
                for band in sector_info["applicable_bands"]:
                    # Generate minimum 10 banks per specialty/band combination
                    for bank_num in range(1, self.min_banks_per_sector + 1):
                        question_bank = self.generate_sector_questions(
                            sector, specialty, band, bank_num
                        )
                        
                        filename = f"{sector}_{specialty}_{band}_bank_{bank_num:02d}.json"
                        filepath = os.path.join(sector_dir, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(question_bank, f, indent=2, ensure_ascii=False)
                        
                        total_banks += 1
                        print(f"✅ Created: {filename} ({question_bank['total_questions']} questions)")
        
        print(f"\n{'='*60}")
        print(f"✨ COMPLETE! Generated {total_banks} question banks")
        print(f"{'='*60}")
        
        # Generate summary
        self._generate_summary(output_base, total_banks)
    
    def _generate_summary(self, output_base: str, total_banks: int):
        """Generate summary of all generated questions"""
        summary = {
            "generation_date": datetime.now().isoformat(),
            "total_question_banks": total_banks,
            "sectors": {},
            "band_structure": {
                "bands": list(self.bands.keys()),
                "note": "No Band 9 - does not exist in practice in NHS"
            }
        }
        
        for sector, sector_info in self.sectors.items():
            num_specialties = len(sector_info["specialties"])
            num_bands = len(sector_info["applicable_bands"])
            sector_banks = num_specialties * num_bands * self.min_banks_per_sector
            
            summary["sectors"][sector] = {
                "name": sector_info["name"],
                "specialties": sector_info["specialties"],
                "applicable_bands": sector_info["applicable_bands"],
                "banks_generated": sector_banks
            }
        
        summary_path = os.path.join(output_base, "generation_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Summary saved to: generation_summary.json")

def main():
    """Main execution"""
    print("="*60)
    print("UK Healthcare Question Generator")
    print("Generating questions for ALL UK healthcare sectors")
    print("="*60)
    print("\nSectors covered:")
    print("✅ NHS Hospitals (all specialties)")
    print("✅ Private Healthcare")
    print("✅ Care Homes & Residential Care")
    print("✅ Community Healthcare")
    print("✅ Primary Care / GP Surgeries")
    print("\nBand structure:")
    print("✅ Band 2, 3, 4, 5, 6, 7")
    print("✅ Band 8a, 8b, 8c, 8d")
    print("❌ NO Band 9 (does not exist in practice)")
    print("\n" + "="*60)
    
    generator = UKHealthcareQuestionGenerator()
    generator.generate_all_questions()
    
    print("\n✨ Generation complete! All question banks created.")

if __name__ == "__main__":
    main()

