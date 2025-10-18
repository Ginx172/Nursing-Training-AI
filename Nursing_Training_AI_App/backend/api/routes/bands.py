from fastapi import APIRouter


router = APIRouter()


BANDS = [
    {"id": "band_6", "name": "Band 6", "description": "Senior Staff Nurse"},
    {"id": "band_7", "name": "Band 7", "description": "Clinical Nurse Specialist"},
    {"id": "band_8a", "name": "Band 8A", "description": "Advanced Nurse Practitioner"},
]


@router.get("/")
async def list_bands():
    return BANDS


