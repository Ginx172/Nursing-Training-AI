"""
Seed Data - NHS Bands
Run: python -m scripts.seed_bands
"""

BANDS = [
    {
        "band_number": "2",
        "title": "Healthcare Assistant (HCA)",
        "description": "Support worker - basic patient care, observations, hygiene, feeding",
        "focus_areas": ["Basic care", "Observations", "Patient hygiene", "Feeding", "Mobility"],
        "management_level": "none",
        "min_experience_years": 0
    },
    {
        "band_number": "3",
        "title": "Senior Healthcare Assistant",
        "description": "Experienced HCA - phlebotomy, ECGs, catheterisation, mentoring junior HCAs",
        "focus_areas": ["Phlebotomy", "ECGs", "Catheterisation", "Basic wound care", "Mentoring HCAs"],
        "management_level": "none",
        "min_experience_years": 1
    },
    {
        "band_number": "4",
        "title": "Assistant Practitioner / Nursing Associate",
        "description": "Bridge between HCA and Registered Nurse - delegated clinical tasks, care planning",
        "focus_areas": ["Care planning", "Medication administration", "Clinical assessments", "Patient education"],
        "management_level": "none",
        "min_experience_years": 2
    },
    {
        "band_number": "5",
        "title": "Staff Nurse (Registered Nurse)",
        "description": "Newly qualified to experienced RN - full clinical responsibility, drug rounds, assessments",
        "focus_areas": ["Clinical skills", "Drug administration", "Patient assessment", "Care coordination", "Documentation", "Safeguarding"],
        "management_level": "none",
        "min_experience_years": 0
    },
    {
        "band_number": "6",
        "title": "Sister / Charge Nurse / Junior Ward Manager",
        "description": "Senior nurse with leadership responsibilities - shift coordination, mentoring, audits",
        "focus_areas": ["Leadership", "Shift coordination", "Mentoring students", "Clinical audits", "Incident reporting", "Safeguarding lead"],
        "management_level": "entry",
        "min_experience_years": 2
    },
    {
        "band_number": "7",
        "title": "Ward Manager / Team Leader",
        "description": "Full ward management - budgets, rosters, governance, complaints, service improvement",
        "focus_areas": ["Ward management", "Budget management", "Roster planning", "Clinical governance", "Complaints handling", "Service improvement", "Staff appraisals", "Audit cycle"],
        "management_level": "mid",
        "min_experience_years": 5
    },
    {
        "band_number": "8a",
        "title": "Matron / Senior Nurse Manager",
        "description": "Multi-ward oversight - strategic planning, quality assurance, infection control lead",
        "focus_areas": ["Strategic planning", "Quality assurance", "Multi-ward management", "Policy development", "CQC readiness", "Patient experience", "Workforce planning"],
        "management_level": "senior",
        "min_experience_years": 8
    },
    {
        "band_number": "8b",
        "title": "Senior Matron / Head of Nursing",
        "description": "Directorate-level nursing leadership - divisional governance, recruitment strategy",
        "focus_areas": ["Divisional governance", "Recruitment strategy", "Training programmes", "Risk management", "Board reporting"],
        "management_level": "senior",
        "min_experience_years": 10
    },
    {
        "band_number": "8c",
        "title": "Associate Director of Nursing",
        "description": "Trust-wide nursing strategy - workforce transformation, quality improvement programmes",
        "focus_areas": ["Trust-wide strategy", "Workforce transformation", "Quality improvement", "External partnerships"],
        "management_level": "senior",
        "min_experience_years": 12
    },
    {
        "band_number": "8d",
        "title": "Deputy Director of Nursing",
        "description": "Deputy to Chief Nurse - trust governance, CQC liaison, national policy implementation",
        "focus_areas": ["Trust governance", "CQC liaison", "National policy", "Board-level reporting"],
        "management_level": "senior",
        "min_experience_years": 15
    },
    {
        "band_number": "9",
        "title": "Director of Nursing / Chief Nurse",
        "description": "Board-level executive - trust-wide clinical strategy, patient safety, professional standards",
        "focus_areas": ["Executive leadership", "Clinical strategy", "Patient safety", "Professional standards", "Board membership"],
        "management_level": "senior",
        "min_experience_years": 18
    },
]

def seed_bands():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from core.database import SessionLocal
    from models.nursing import Band

    db = SessionLocal()
    added = 0
    skipped = 0

    try:
        for band in BANDS:
            existing = db.query(Band).filter_by(band_number=band["band_number"]).first()
            if existing:
                skipped += 1
                continue
            db.add(Band(**band))
            added += 1

        db.commit()
        print(f"Bands seeded: {added} added, {skipped} skipped (already exist)")
        print(f"Total in DB: {db.query(Band).count()}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_bands()
