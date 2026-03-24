from dotenv import load_dotenv
import os

# Load .env BEFORE importing regional modules/services
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router as triage_router

app = FastAPI(
    title="VITA - AI-powered Voice-Enabled Digital Family Doctor",
    description="AI Clinical Triage API for text and voice symptom inputs.",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register API routes
app.include_router(triage_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    n8n_url = os.getenv("N8N_WEBHOOK_URL", "not configured")
    return {
        "status": "ok",
        "message": "VITA Engine is running.",
        "n8n_webhook": n8n_url,
        "env_path": env_path,
        "env_exists": os.path.exists(env_path)
    }

@app.get("/")
def serve_ui():
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path)
