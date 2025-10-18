from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os
import json
import re

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'question_banks')
CURATED_DIR = os.path.join(DATA_DIR, 'curated')
BANK_FILE_RE = re.compile(r'^(?P<specialty>.+)_(?P<band>band_[0-9]+)_bank_(?P<num>[0-9]{2})\.json$')

class AutoPresentationResponse(BaseModel):
    app_name: str
    capabilities: Dict[str, Any]
    datasets: Dict[str, Any]
    security: Dict[str, Any]
    ai_stack: Dict[str, Any]

@router.get("/summary", response_model=AutoPresentationResponse)
async def auto_presentation_summary():
    # Collect datasets stats
    if not os.path.isdir(DATA_DIR):
        raise HTTPException(status_code=500, detail='Question banks directory not found')

    stats = {
        'total_files': 0,
        'specialties': {},
        'bands': {},
        'banks_per_specialty_band': {},
        'question_counts_by_band': {},
        'curated_count': 0
    }

    if os.path.isdir(CURATED_DIR):
        try:
            stats['curated_count'] = len([n for n in os.listdir(CURATED_DIR) if n.endswith('.json')])
        except Exception:
            stats['curated_count'] = 0

    for name in os.listdir(DATA_DIR):
        if not name.endswith('.json'):
            continue
        m = BANK_FILE_RE.match(name)
        if not m:
            continue
        stats['total_files'] += 1
        spec = m.group('specialty')
        band = m.group('band')
        key = f"{spec}_{band}"
        stats['specialties'][spec] = stats['specialties'].get(spec, 0) + 1
        stats['bands'][band] = stats['bands'].get(band, 0) + 1
        stats['banks_per_specialty_band'][key] = stats['banks_per_specialty_band'].get(key, 0) + 1
        # Read total_questions once per file to infer band typical counts
        try:
            with open(os.path.join(DATA_DIR, name), 'r', encoding='utf-8') as f:
                data = json.load(f)
                tq = data.get('total_questions')
                if isinstance(tq, int):
                    arr = stats['question_counts_by_band'].setdefault(band, [])
                    if len(arr) < 10:
                        arr.append(tq)
        except Exception:
            pass

    # Capabilities and stack
    openai_enabled = bool(os.getenv('OPENAI_API_KEY'))
    mcp_endpoint = os.getenv('MCP_ENDPOINT')
    rag_endpoint = os.getenv('RAG_ENDPOINT')
    stripe_webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    capabilities = {
        'bands_supported': sorted(list(stats['bands'].keys())),
        'specialties_supported': sorted(list(stats['specialties'].keys())),
        'banks_per_specialty': 30,
        'max_overlap_between_consecutive_banks': '20% of questions',
        'ai_evaluation': True,
        'rag_knowledge_access': bool(rag_endpoint),
        'mcp_multi_criteria': bool(mcp_endpoint),
        'book_recommendations': True,
        'audio_stt': openai_enabled,
        'audio_tts': openai_enabled,
        'payment_verification': True,
        'audit_trails': True,
        'self_learning': True,
        'telemetry': True,
        'security_hardening': True
    }

    security = {
        'headers_csp': True,
        'rate_limiting': True,
        'ip_filtering': True,
        'signature_verification_stripe': bool(stripe_webhook_secret),
        'anomaly_detection': True,
        'input_sanitization': True,
        'encryption': True
    }

    ai_stack = {
        'mcp_endpoint': mcp_endpoint,
        'rag_endpoint': rag_endpoint,
        'openai_available': openai_enabled,
        'evaluation_universal': True
    }

    return AutoPresentationResponse(
        app_name='Nursing Training AI - UK Healthcare',
        capabilities=capabilities,
        datasets={
            'total_banks': stats['total_files'],
            'curated_banks': stats['curated_count'],
            'specialty_counts': stats['specialties'],
            'band_counts': stats['bands'],
            'banks_per_specialty_band': stats['banks_per_specialty_band'],
            'question_counts_by_band_samples': stats['question_counts_by_band']
        },
        security=security,
        ai_stack=ai_stack
    )
