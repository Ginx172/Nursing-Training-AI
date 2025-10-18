from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import re

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'question_banks')
CURATED_DIR = os.path.join(DATA_DIR, 'curated')

# Regex for filenames like: {specialty}_{band}_bank_{NN}.json
BANK_FILE_RE = re.compile(r'^(?P<specialty>.+)_(?P<band>band_[0-9]+)_bank_(?P<num>[0-9]{2})\.json$')

class BankItem(BaseModel):
    filename: str
    specialty: str
    band: str
    bank_number: int
    version: Optional[str] = None
    total_questions: Optional[int] = None

class BankListResponse(BaseModel):
    items: List[BankItem]
    total: int
    page: int
    page_size: int

@router.get('/catalog', response_model=BankListResponse)
async def list_banks(
    specialty: Optional[str] = Query(None, description='Filter by specialty id (e.g., amu, cardiology, mental_health)'),
    band: Optional[str] = Query(None, description='Filter by band id (e.g., band_5)'),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200)
):
    if not os.path.isdir(DATA_DIR):
        raise HTTPException(status_code=500, detail='Question banks directory not found')

    entries: List[BankItem] = []
    for name in os.listdir(DATA_DIR):
        if not name.endswith('.json'):
            continue
        m = BANK_FILE_RE.match(name)
        if not m:
            continue
        spec = m.group('specialty')
        band_id = m.group('band')
        num = int(m.group('num'))
        if specialty and spec.lower() != specialty.lower():
            continue
        if band and band_id.lower() != band.lower():
            continue

        version = None
        total_questions = None
        try:
            with open(os.path.join(DATA_DIR, name), 'r', encoding='utf-8') as f:
                data = json.load(f)
                version = data.get('version')
                total_questions = data.get('total_questions')
        except Exception:
            pass
        entries.append(BankItem(filename=name, specialty=spec, band=band_id, bank_number=num, version=version, total_questions=total_questions))

    entries.sort(key=lambda x: (x.specialty, x.band, x.bank_number))
    total = len(entries)
    start = (page - 1) * page_size
    end = start + page_size
    paged = entries[start:end]
    return BankListResponse(items=paged, total=total, page=page, page_size=page_size)

class CuratedItem(BaseModel):
    filename: str

@router.get('/curated', response_model=List[CuratedItem])
async def list_curated():
    if not os.path.isdir(CURATED_DIR):
        return []
    items: List[CuratedItem] = []
    for name in os.listdir(CURATED_DIR):
        if name.endswith('.json'):
            items.append(CuratedItem(filename=name))
    items.sort(key=lambda x: x.filename)
    return items
