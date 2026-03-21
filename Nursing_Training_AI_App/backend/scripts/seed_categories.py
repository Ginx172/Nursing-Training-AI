"""
Seed Data - Question Categories
Run: python -m scripts.seed_categories
"""

CATEGORIES = [
    {
        "name": "Clinical Knowledge",
        "description": "BLS/ALS, medications, clinical assessments, NEWS2, ABCDE, patient deterioration",
        "applies_from_band": "2"
    },
    {
        "name": "Safeguarding",
        "description": "Safeguarding adults and children, DOLS, MCA, duty of candour, whistleblowing",
        "applies_from_band": "2"
    },
    {
        "name": "Communication & Teamwork",
        "description": "SBAR handover, MDT working, patient communication, breaking bad news, conflict resolution",
        "applies_from_band": "2"
    },
    {
        "name": "Ethics & Professional Standards",
        "description": "NMC Code, consent, confidentiality, Gillick competence, professional boundaries",
        "applies_from_band": "2"
    },
    {
        "name": "Patient Safety & Risk Management",
        "description": "Incident reporting, root cause analysis, risk assessments, falls prevention, pressure ulcers",
        "applies_from_band": "2"
    },
    {
        "name": "Infection Prevention & Control",
        "description": "Hand hygiene, PPE, isolation protocols, MRSA, C.diff, sepsis recognition",
        "applies_from_band": "2"
    },
    {
        "name": "Equality, Diversity & Inclusion",
        "description": "Cultural competence, unconscious bias, reasonable adjustments, protected characteristics",
        "applies_from_band": "2"
    },
    {
        "name": "Motivation & Values",
        "description": "Why nursing, career aspirations, NHS values, 6Cs (Care, Compassion, Competence, Communication, Courage, Commitment)",
        "applies_from_band": "2"
    },
    {
        "name": "Scenario-Based / Situational",
        "description": "What would you do if... scenarios - ethical dilemmas, emergency situations, team conflicts",
        "applies_from_band": "2"
    },
    {
        "name": "Leadership & Management",
        "description": "Delegation, team leadership, shift coordination, mentoring, preceptorship",
        "applies_from_band": "6"
    },
    {
        "name": "Clinical Governance & Audits",
        "description": "Audit cycle, evidence-based practice, NICE guidelines, clinical effectiveness, quality improvement",
        "applies_from_band": "7"
    },
    {
        "name": "Budget & Resource Management",
        "description": "Budget management, roster planning, skill mix, agency spend, resource allocation",
        "applies_from_band": "7"
    },
    {
        "name": "Service Improvement & Strategy",
        "description": "PDSA cycles, change management, CQC standards, KPIs, patient experience improvement",
        "applies_from_band": "7"
    },
    {
        "name": "Complaints & Investigations",
        "description": "PALS, formal complaints, serious incidents (SI), duty of candour, learning from incidents",
        "applies_from_band": "6"
    },
    {
        "name": "Trust Values & NHS Constitution",
        "description": "Trust-specific values, NHS Constitution rights, patient-centred care, organisational culture",
        "applies_from_band": "2"
    },
]

def seed_categories():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from core.database import SessionLocal
    from models.nursing import QuestionCategory

    db = SessionLocal()
    added = 0
    skipped = 0

    try:
        for cat in CATEGORIES:
            existing = db.query(QuestionCategory).filter_by(name=cat["name"]).first()
            if existing:
                skipped += 1
                continue
            db.add(QuestionCategory(**cat))
            added += 1

        db.commit()
        print(f"Categories seeded: {added} added, {skipped} skipped (already exist)")
        print(f"Total in DB: {db.query(QuestionCategory).count()}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_categories()
