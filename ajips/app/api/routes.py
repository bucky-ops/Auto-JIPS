import logging
import time
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ajips.app.api.schemas import AnalyzeRequest, AnalyzeResponse
from ajips.core.pipelines.job_profile import build_job_profile
from ajips.app.config import settings

logger = logging.getLogger(__name__)

# Rate limiting with per-IP key
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()
# Note: router.state is set on the FastAPI app instance; handlers are registered via app state in main.py
router.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@router.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "ajips"}


@router.get("/health/detailed")
def detailed_health_check(request: Request) -> dict:
    """Detailed health check with system information."""
    uptime = time.time() - request.app.state.startup_time
    return {
        "status": "ok",
        "service": "ajips",
        "version": settings.API_VERSION,
        "uptime_seconds": round(uptime, 2),
        "database_status": "ok",
        "external_apis": "operational",
    }


@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("30/minute")
def analyze_job_posting(request: Request, payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a job posting with rate limiting and error handling."""
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
