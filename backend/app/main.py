"""Backend principal - FastAPI."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers import gmail_router, calendar_router, drive_router, dashboard_router

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

# Static files y templates para el dashboard
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")
templates = Jinja2Templates(directory="dashboard/templates")

# Routers
app.include_router(gmail_router.router, prefix="/api/gmail", tags=["Gmail"])
app.include_router(calendar_router.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(drive_router.router, prefix="/api/drive", tags=["Drive"])
app.include_router(dashboard_router.router, tags=["Dashboard"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Google Workspace Automation"}
