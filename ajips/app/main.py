import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pythonjsonlogger import jsonlogger

from ajips.app.api.routes import router as api_router

# Configure JSON structured logging for production
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(name)s %(levelname)s %(message)s"
)
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logHandler)

app = FastAPI(
    title="AJIPS - Automated Job Intelligence Profiling System",
    version="1.1.0",
    description="Analyze job postings with AI-powered insights",
)

# Restrict CORS to safe origins; adjust for your deployment in production
ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    # Add your production domains here, e.g., "https://ajips.example.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time

    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        "request_processed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2),
            "client_ip": request.client.host if request.client else None,
        },
    )
    return response


# Serve static files (UI)
ui_path = Path(__file__).parent.parent / "ui"
if ui_path.exists():
    app.mount("/static", StaticFiles(directory=str(ui_path)), name="static")

    @app.get("/")
    async def serve_ui():
        """Serve the main UI page"""
        return FileResponse(str(ui_path / "index.html"))


@app.get("/version")
def version() -> dict:
    """Version and build info endpoint for health checks."""
    return {"version": "1.1.0", "name": "AJIPS"}
