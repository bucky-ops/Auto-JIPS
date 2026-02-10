import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from ajips.app.api.schemas import AnalyzeRequest, AnalyzeResponse
from ajips.core.pipelines.job_profile import build_job_profile

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_job_posting(payload: AnalyzeRequest) -> AnalyzeResponse:
    try:
        profile = build_job_profile(payload)
        return profile
    except ValueError as ve:
        logger.warning(f"Invalid input: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        logger.error(f"Analysis failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal server error during analysis"
        )
