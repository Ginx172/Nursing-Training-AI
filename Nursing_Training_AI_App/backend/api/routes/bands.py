from fastapi import APIRouter


router = APIRouter()


BANDS = [
    {"id": "band_2", "name": "Band 2", "description": "Healthcare Assistant"},
    {"id": "band_3", "name": "Band 3", "description": "Senior Healthcare Assistant"},
    {"id": "band_4", "name": "Band 4", "description": "Assistant Practitioner"},
    {"id": "band_5", "name": "Band 5", "description": "Staff Nurse"},
    {"id": "band_6", "name": "Band 6", "description": "Senior Staff Nurse"},
    {"id": "band_7", "name": "Band 7", "description": "Clinical Nurse Specialist"},
    {"id": "band_8a", "name": "Band 8A", "description": "Advanced Nurse Practitioner"},
    {"id": "band_8b", "name": "Band 8B", "description": "Senior Advanced Nurse Practitioner"},
    {"id": "band_8c", "name": "Band 8C", "description": "Consultant Nurse"},
    {"id": "band_8d", "name": "Band 8D", "description": "Senior Consultant Nurse"},
    {"id": "band_9", "name": "Band 9", "description": "Director of Nursing"},
]


@router.get("/")
async def list_bands():
    return BANDS


