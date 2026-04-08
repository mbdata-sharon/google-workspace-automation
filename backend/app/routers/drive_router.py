"""API endpoints para Google Drive."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from automations.drive_automation import DriveAutomation

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    max_results: int = 10


@router.get("/recent")
def get_recent_files(max_results: int = 10):
    """Lista archivos recientes."""
    try:
        drive = DriveAutomation()
        return {"files": drive.list_recent_files(max_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
def search_files(request: SearchRequest):
    """Busca archivos en Drive."""
    try:
        drive = DriveAutomation()
        return {"files": drive.search_files(request.query, request.max_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/storage")
def get_storage_info():
    """Información del almacenamiento."""
    try:
        drive = DriveAutomation()
        return drive.get_storage_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
