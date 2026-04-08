"""Rutas del dashboard web."""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="dashboard/templates")


@router.get("/")
def dashboard_home(request: Request):
    """Página principal del dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})
