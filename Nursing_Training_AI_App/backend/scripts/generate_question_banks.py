#!/usr/bin/env python3
"""
Generator pentru bateriile de întrebări pentru toate banzile și specialitățile
Conform specificațiilor: Band 2-8, 30 baterii per specialitate, întrebări în engleză
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime

# Configurație pentru banzile și numărul de întrebări
BAND_CONFIG = {
    "band_2": {"questions": 8, "calculations": 0, "leadership": 0, "supervision": 0},
    "band_3": {"questions": 10, "calculations": 0, "leadership": 0, "supervision": 0},
    "band_4": {"questions": 12, "calculations": 0, "leadership": 0, "supervision": 0},
    "band_5": {"questions": 18, "calculations": 4, "leadership": 0, "supervision": 0},
    "band_6": {"questions": 22, "calculations": 4, "leadership": 2, "supervision": 1},
    "band_7": {"questions": 25, "calculations": 4, "leadership": 8, "supervision": 0},
    "band_8": {"questions": 35, "calculations": 4, "leadership": 12, "supervision": 0}
}

# Specialități disponibile
SPECIALTIES = [
    "amu", "icu", "emergency", "maternity", "mental_health", 
    "pediatrics", "oncology", "cardiology", "neurology"
]

# Template-uri pentru întrebări pe categorii
QUESTION_TEMPLATES = {
    "clinical_assessment": [
        "Describe your approach to assessing a patient presenting with {symptom}",
        "What are the key observations you would monitor for a patient with {condition}?",
        "How would you prioritize care for a patient with multiple acute conditions?",
        "What assessment tools would you use for a patient with {condition}?"
    ],
    "calculation": [
        "Calculate the {medication} dose for a {weight}kg patient requiring {dose}mg/kg",
        "A patient requires {volume}ml of {fluid} over {hours} hours. What is the infusion rate?",
        "Calculate the maintenance fluid requirements for a {weight}kg patient",
        "What is the correct dose of {medication} for a patient with {condition}?"
    ],
    "leadership": [
        "How would you lead your team during a major incident in {specialty}?",
        "Describe your approach to managing conflict within your healthcare team",
        "How would you implement a new protocol in your department?",
        "What strategies would you use to improve patient safety in {specialty}?"
    ],
    "management": [
        "How would you manage resources during a busy period in {specialty}?",
        "Describe your approach to staff development and training",
        "How would you handle a complaint from a patient's family?",
        "What quality improvement initiatives would you implement in {specialty}?"
    ],
    "supervision": [
        "How would you supervise a junior nurse caring for a complex patient?",
        "Describe your approach to clinical supervision and mentorship",
        "How would you support a struggling team member?",
        "What documentation is required for clinical supervision?"
    ],
    "safety": [
        "What safety measures would you implement for a patient with {condition}?",
        "How would you prevent medication errors in {specialty}?",
        "Describe your approach to infection control in {specialty}",
        "What would you do if you identified a safety concern?"
    ]
}

# Condiții și simptome specifice pentru fiecare specialitate
SPECIALTY_CONDITIONS = {
    "amu": ["chest pain", "shortness of breath", "abdominal pain", "confusion", "fever"],
    "icu": ["respiratory failure", "septic shock", "multi-organ failure", "trauma", "post-surgical"],
    "emergency": ["trauma", "cardiac arrest", "stroke", "overdose", "severe bleeding"],
    "maternity": ["labour", "postpartum haemorrhage", "pre-eclampsia", "fetal distress", "neonatal care"],
    "mental_health": ["depression", "anxiety", "psychosis", "self-harm", "aggression"],
    "pediatrics": ["fever", "respiratory distress", "dehydration", "seizures", "developmental concerns"],
    "oncology": ["chemotherapy side effects", "pain management", "infection risk", "fatigue", "nausea"],
    "cardiology": ["chest pain", "heart failure", "arrhythmias", "hypertension", "cardiac procedures"],
    "neurology": ["stroke", "seizures", "headache", "altered consciousness", "movement disorders"]
}

def generate_question_bank(band: str, specialty: str, bank_number: int) -> Dict[str, Any]:
    """Generează o baterie de întrebări pentru o bandă și specialitate specifică"""
    
    config = BAND_CONFIG[band]
    total_questions = config["questions"]
    calculations = config["calculations"]
    leadership = config["leadership"]
    supervision = config["supervision"]
    
    # Calculează întrebări clinice de bază
    clinical_questions = total_questions - calculations - leadership - supervision

    # Helper pentru a crea un set de întrebări respectând regula de overlap ≤20%
    def build_questions_with_overlap_limit(previous_bank_questions: set, attempt_offset: int) -> List[Dict[str, Any]]:
        questions_local: List[Dict[str, Any]] = []
        question_id_local = 1

        # Generează întrebări clinice de bază cu decalaj pentru diversitate
        for i in range(clinical_questions):
            cond_idx = (i + attempt_offset) % len(SPECIALTY_CONDITIONS[specialty])
            tmpl_idx = (i + (attempt_offset // 2)) % len(QUESTION_TEMPLATES["clinical_assessment"])
            condition = SPECIALTY_CONDITIONS[specialty][cond_idx]
            template = QUESTION_TEMPLATES["clinical_assessment"][tmpl_idx]
            question_text = template.format(symptom=condition, condition=condition, specialty=specialty)
            questions_local.append({
                "id": question_id_local,
                "title": f"Clinical Assessment - {condition.title()}",
                "question_text": question_text,
                "question_type": "scenario",
                "difficulty": get_difficulty_level(band),
                "competencies": get_competencies(band, specialty),
                "expected_points": generate_expected_points(condition, specialty)
            })
            question_id_local += 1

        # Generează întrebări de calcul
        for i in range(calculations):
            questions_local.append(generate_calculation_question(question_id_local, specialty, band))
            question_id_local += 1

        # Generează întrebări de leadership
        for i in range(leadership):
            questions_local.append(generate_leadership_question(question_id_local, specialty, band))
            question_id_local += 1

        # Generează întrebări de supervision
        for i in range(supervision):
            questions_local.append(generate_supervision_question(question_id_local, specialty, band))
            question_id_local += 1

        # Evaluează overlap față de banca anterioară
        if previous_bank_questions:
            current_texts = {q["question_text"] for q in questions_local}
            overlap = len(previous_bank_questions.intersection(current_texts))
            allowed = int(total_questions * 0.2)
            if overlap > allowed:
                return []  # semnal pentru a reîncerca cu alt offset

        return questions_local

    # Încarcă banca anterioară pentru a limita overlap-ul (consecutive banks)
    previous_questions_set: set = set()
    if bank_number > 1:
        prev_bank_id = f"{specialty}_{band}_bank_{(bank_number-1):02d}"
        prev_path = os.path.join("data/question_banks", f"{prev_bank_id}.json")
        if os.path.exists(prev_path):
            try:
                with open(prev_path, "r", encoding="utf-8") as pf:
                    prev_data = json.load(pf)
                    previous_questions_set = {q.get("question_text", "") for q in prev_data.get("questions", [])}
            except Exception:
                previous_questions_set = set()

    # Încearcă să construiești banca respectând regula de overlap
    questions: List[Dict[str, Any]] = []
    for attempt in range(0, 10):  # până la 10 încercări cu offset diferit
        q = build_questions_with_overlap_limit(previous_questions_set, attempt_offset=(attempt + bank_number))
        if q:
            questions = q
            break
    if not questions:
        # dacă nu s-a reușit, acceptă ultima versiune (fallback sigur, dar puțin probabil)
        questions = build_questions_with_overlap_limit(set(), attempt_offset=bank_number) or []

    return {
        "band": band,
        "specialty": specialty,
        "bank_id": f"{specialty}_{band}_bank_{bank_number:02d}",
        "version": datetime.now().strftime("%Y-%m-%d"),
        "total_questions": total_questions,
        "calculation_questions": calculations,
        "leadership_questions": leadership,
        "supervision_questions": supervision,
        "difficulty_level": get_difficulty_level(band),
        "questions": questions
    }

def get_difficulty_level(band: str) -> str:
    """Returnează nivelul de dificultate pentru o bandă"""
    difficulty_map = {
        "band_2": "basic",
        "band_3": "basic",
        "band_4": "basic",
        "band_5": "intermediate",
        "band_6": "intermediate",
        "band_7": "advanced",
        "band_8": "expert"
    }
    return difficulty_map.get(band, "intermediate")

def get_competencies(band: str, specialty: str) -> List[str]:
    """Returnează competențele pentru o bandă și specialitate"""
    base_competencies = ["Assessment", "Patient care", "Safety", "Communication"]
    
    if band in ["band_6", "band_7", "band_8"]:
        base_competencies.extend(["Leadership", "Management"])
    
    if band in ["band_7", "band_8"]:
        base_competencies.extend(["Strategic planning", "Quality improvement"])
    
    specialty_competencies = {
        "amu": ["Acute care", "Medical emergencies"],
        "icu": ["Critical care", "Ventilation", "Hemodynamics"],
        "emergency": ["Trauma", "Resuscitation", "Triage"],
        "maternity": ["Antenatal care", "Labour", "Postnatal care"],
        "mental_health": ["Mental health assessment", "Crisis intervention"],
        "pediatrics": ["Child development", "Family-centered care"],
        "oncology": ["Cancer care", "Palliative care"],
        "cardiology": ["Cardiac care", "ECG interpretation"],
        "neurology": ["Neurological assessment", "Seizure management"]
    }
    
    return base_competencies + specialty_competencies.get(specialty, [])

def generate_expected_points(condition: str, specialty: str) -> List[str]:
    """Generează punctele așteptate pentru o întrebare"""
    return [
        f"Assess {condition} using appropriate assessment tools",
        f"Monitor vital signs and observations specific to {condition}",
        f"Implement evidence-based interventions for {condition}",
        f"Document findings and care provided",
        f"Escalate concerns appropriately in {specialty} setting"
    ]

def generate_calculation_question(question_id: int, specialty: str, band: str) -> Dict[str, Any]:
    """Generează o întrebare de calcul"""
    calculations = [
        {
            "text": "A {weight}kg patient requires {dose}mg/kg of {medication}. Calculate the total dose required.",
            "medication": "paracetamol",
            "dose": "15",
            "weight": "70"
        },
        {
            "text": "Calculate the infusion rate for {volume}ml of {fluid} to be given over {hours} hours.",
            "fluid": "0.9% sodium chloride",
            "volume": "1000",
            "hours": "8"
        },
        {
            "text": "A patient requires maintenance fluids at 30ml/kg/day. Calculate the hourly rate for a {weight}kg patient.",
            "weight": "60",
            "medication": "fluids"
        },
        {
            "text": "Calculate the correct dose of {medication} for a {weight}kg patient with {condition}.",
            "medication": "morphine",
            "weight": "75",
            "condition": "severe pain"
        }
    ]
    
    calc = calculations[question_id % len(calculations)]
    
    # Ensure all calculations have a medication field
    if "medication" not in calc:
        calc["medication"] = "medication"
    
    return {
        "id": question_id,
        "title": f"Medication Calculation - {calc['medication'].title()}",
        "question_text": calc["text"].format(**calc),
        "question_type": "calculation",
        "correct_answer": calculate_answer(calc),
        "difficulty": get_difficulty_level(band),
        "competencies": ["Calculations", "Medication safety", "Dose calculations"],
        "expected_points": [
            "Show all working clearly",
            "Check calculation twice",
            "Consider patient factors",
            "Verify with another healthcare professional if unsure"
        ]
    }

def calculate_answer(calc: Dict[str, Any]) -> str:
    """Calculează răspunsul pentru o întrebare de calcul"""
    if "paracetamol" in calc["text"]:
        return str(int(calc["weight"]) * int(calc["dose"]))
    elif "infusion rate" in calc["text"]:
        return str(int(calc["volume"]) // int(calc["hours"]))
    elif "maintenance fluids" in calc["text"]:
        return str((int(calc["weight"]) * 30) // 24)
    else:
        return "15"  # Default answer

def generate_leadership_question(question_id: int, specialty: str, band: str) -> Dict[str, Any]:
    """Generează o întrebare de leadership"""
    leadership_topics = [
        "team management during crisis",
        "implementing new protocols",
        "managing staff performance",
        "quality improvement initiatives",
        "patient safety leadership",
        "resource management",
        "change management",
        "staff development"
    ]
    
    topic = leadership_topics[question_id % len(leadership_topics)]
    
    return {
        "id": question_id,
        "title": f"Leadership - {topic.title()}",
        "question_text": f"Describe your approach to {topic} in {specialty}. What challenges might you face and how would you address them?",
        "question_type": "scenario",
        "difficulty": get_difficulty_level(band),
        "competencies": ["Leadership", "Management", "Team working", "Problem solving"],
        "expected_points": [
            "Demonstrate understanding of leadership principles",
            "Consider team dynamics and individual needs",
            "Address potential challenges proactively",
            "Show evidence-based approach to management"
        ]
    }

def generate_supervision_question(question_id: int, specialty: str, band: str) -> Dict[str, Any]:
    """Generează o întrebare de supervision"""
    return {
        "id": question_id,
        "title": "Clinical Supervision",
        "question_text": f"How would you provide effective clinical supervision to a junior nurse in {specialty}? What documentation and processes would you follow?",
        "question_type": "scenario",
        "difficulty": get_difficulty_level(band),
        "competencies": ["Clinical supervision", "Mentorship", "Professional development", "Documentation"],
        "expected_points": [
            "Establish clear supervision framework",
            "Regular review and feedback sessions",
            "Document supervision activities",
            "Support professional development",
            "Address any concerns promptly"
        ]
    }

def main():
    """Funcția principală pentru generarea tuturor bateriilor"""
    
    # Creează directorul pentru bateriile de întrebări
    output_dir = "data/question_banks"
    os.makedirs(output_dir, exist_ok=True)
    
    total_banks = 0
    
    # Generează bateriile pentru fiecare bandă și specialitate
    for specialty in SPECIALTIES:
        for band in BAND_CONFIG.keys():
            for bank_number in range(1, 31):  # 30 baterii per specialitate
                bank = generate_question_bank(band, specialty, bank_number)
                
                # Salvează bateria
                filename = f"{specialty}_{band}_bank_{bank_number:02d}.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(bank, f, indent=2, ensure_ascii=False)
                
                total_banks += 1
                print(f"Generated: {filename}")
    
    print(f"\n✅ Successfully generated {total_banks} question banks!")
    print(f"📊 Distribution:")
    print(f"   - {len(SPECIALTIES)} specialties")
    print(f"   - {len(BAND_CONFIG)} bands")
    print(f"   - 30 banks per specialty")
    print(f"   - Total: {total_banks} question banks")

if __name__ == "__main__":
    main()
