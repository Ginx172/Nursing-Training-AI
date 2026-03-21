"""
Seed Data - NHS Specialities
Run: python -m scripts.seed_specialities
"""

SPECIALITIES = [
    {"code": "ae", "name": "Accident & Emergency (A&E)", "description": "Emergency department - triage, resuscitation, trauma, acute care"},
    {"code": "medical", "name": "Medical Ward", "description": "General medical conditions - respiratory, gastro, endocrine, neurology"},
    {"code": "surgical", "name": "Surgical Ward", "description": "Pre-operative and post-operative surgical patient care"},
    {"code": "icu", "name": "Intensive Care Unit (ICU/ITU)", "description": "Critical care - ventilated patients, multi-organ support, invasive monitoring"},
    {"code": "hdu", "name": "High Dependency Unit (HDU)", "description": "Step-down from ICU - close monitoring, NIV, vasopressors"},
    {"code": "mental_health", "name": "Mental Health", "description": "Psychiatric nursing - acute, community, CAMHS, crisis intervention"},
    {"code": "paediatrics", "name": "Paediatrics", "description": "Children and young people nursing - neonates to adolescents"},
    {"code": "neonatal", "name": "Neonatal Unit (NICU/SCBU)", "description": "Premature and sick newborn care - incubators, ventilation, feeding"},
    {"code": "maternity", "name": "Maternity / Obstetrics", "description": "Antenatal, intrapartum, postnatal care - midwifery support"},
    {"code": "community", "name": "Community Nursing", "description": "District nursing, health visiting, school nursing, community clinics"},
    {"code": "oncology", "name": "Oncology / Haematology", "description": "Cancer care - chemotherapy, radiotherapy, palliative, blood disorders"},
    {"code": "palliative", "name": "Palliative Care / End of Life", "description": "Symptom management, comfort care, family support, syringe drivers"},
    {"code": "orthopaedics", "name": "Orthopaedics / Trauma", "description": "Fractures, joint replacements, traction, mobility rehabilitation"},
    {"code": "cardiology", "name": "Cardiology / Cardiac Care", "description": "Heart conditions - CCU, post-MI, heart failure, cardiac rehab"},
    {"code": "neurology", "name": "Neurology / Neurosurgery", "description": "Stroke, epilepsy, MS, brain/spinal surgery, neuro observations"},
    {"code": "renal", "name": "Renal / Dialysis", "description": "Kidney disease - haemodialysis, peritoneal dialysis, transplant care"},
    {"code": "respiratory", "name": "Respiratory Medicine", "description": "COPD, asthma, pneumonia, chest drains, NIV, oxygen therapy"},
    {"code": "gastro", "name": "Gastroenterology", "description": "GI conditions - endoscopy, liver disease, IBD, stoma care"},
    {"code": "theatre", "name": "Theatre / Recovery / Anaesthetics", "description": "Scrub, circulating, anaesthetic assistance, PACU recovery"},
    {"code": "elderly", "name": "Care of the Elderly / Geriatrics", "description": "Dementia, falls, frailty, rehabilitation, discharge planning"},
    {"code": "dermatology", "name": "Dermatology", "description": "Skin conditions - wound care, tissue viability, leg ulcers"},
    {"code": "ent", "name": "ENT (Ear, Nose & Throat)", "description": "ENT surgery, tracheostomy care, hearing, balance disorders"},
    {"code": "ophthalmology", "name": "Ophthalmology", "description": "Eye conditions - cataract surgery, glaucoma, eye emergencies"},
    {"code": "diabetes", "name": "Diabetes & Endocrinology", "description": "Insulin management, DKA, thyroid, diabetic foot care"},
    {"code": "infection_control", "name": "Infection Prevention & Control", "description": "MRSA, C.diff, sepsis, isolation protocols, hand hygiene audits"},
    {"code": "learning_disability", "name": "Learning Disability Nursing", "description": "Complex needs, communication, behaviour support, safeguarding"},
    {"code": "sexual_health", "name": "Sexual Health / GUM", "description": "STI screening, contraception, HIV care, health promotion"},
    {"code": "occupational_health", "name": "Occupational Health", "description": "Staff health, needle stick injuries, vaccinations, fitness to work"},
    {"code": "ambulatory", "name": "Ambulatory Care / Day Surgery", "description": "Same-day procedures, minor ops, infusion clinics"},
    {"code": "prison", "name": "Prison / Forensic Nursing", "description": "Offender healthcare, mental health in custody, substance misuse"},
]

def seed_specialities():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from core.database import SessionLocal
    from models.nursing import Speciality

    db = SessionLocal()
    added = 0
    skipped = 0

    try:
        for spec in SPECIALITIES:
            existing = db.query(Speciality).filter_by(code=spec["code"]).first()
            if existing:
                skipped += 1
                continue
            db.add(Speciality(**spec))
            added += 1

        db.commit()
        print(f"Specialities seeded: {added} added, {skipped} skipped (already exist)")
        print(f"Total in DB: {db.query(Speciality).count()}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_specialities()
