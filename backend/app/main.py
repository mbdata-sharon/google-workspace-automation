"""Backend principal - FastAPI."""

import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers import gmail_router, calendar_router, drive_router

app = FastAPI(
    title="Google Workspace Automation",
    description="Automatiza tus tareas diarias de Google Workspace con IA",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files y templates
app.mount("/static", StaticFiles(directory=os.path.join(ROOT_DIR, "dashboard", "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(ROOT_DIR, "dashboard", "templates"))

# API Routers
app.include_router(gmail_router.router, prefix="/api/gmail", tags=["Gmail"])
app.include_router(calendar_router.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(drive_router.router, prefix="/api/drive", tags=["Drive"])


@app.get("/", include_in_schema=False)
def dashboard_home(request: Request):
    """Página principal del dashboard."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Google Workspace Automation"}
