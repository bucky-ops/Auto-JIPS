from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from ajips.app.api.routes import router as api_router

app = FastAPI(
    title="AJIPS - Automated Job Intelligence Profiling System",
    version="1.0.0",
    description="Analyze job postings with AI-powered insights"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Serve static files (UI)
ui_path = Path(__file__).parent.parent / "ui"
if ui_path.exists():
    app.mount("/static", StaticFiles(directory=str(ui_path)), name="static")
    
    @app.get("/")
    async def serve_ui():
        """Serve the main UI page"""
        return FileResponse(str(ui_path / "index.html"))

