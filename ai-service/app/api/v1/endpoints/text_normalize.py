"""
text_normalize.py - FastAPI Endpoint Router for Stage 35 Multilingual & Noisy Text Normalization (/api/v1/text/normalize).
"""

import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.multilingual_processor import MultilingualProcessor
from app.schemas import TextNormalizeRequestSchema, MultilingualNormalizationResultSchema

router = APIRouter()

# Global processor instance (singleton)
_processor_instance: Optional[MultilingualProcessor] = None

def get_multilingual_processor() -> MultilingualProcessor:
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = MultilingualProcessor()
    return _processor_instance


@router.post(
    "/normalize",
    response_model=MultilingualNormalizationResultSchema,
    status_code=status.HTTP_200_OK,
    summary="Normalize Multilingual & Noisy Field Safety Report Text",
    description="Normalizes Hinglish, Roman Hindi, spelling mistakes, shorthand, and domain abbreviations while preserving negations, numbers, and asset IDs."
)
def normalize_text(body: TextNormalizeRequestSchema):
    processor = get_multilingual_processor()
    return processor.normalize_text(body.text)
