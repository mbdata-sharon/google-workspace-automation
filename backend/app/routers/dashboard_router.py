"""Rutas del dashboard web."""

import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "dashboard", "templates"))


@router.get("/")
def dashboard_home(request: Request):
    """Página principal del dashboard."""
    return templates.TemplateResponse(request=request, name="index.html")
