"""API endpoints para Google Calendar."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from automations.calendar_automation import CalendarAutomation

router = APIRouter()


class CreateEventRequest(BaseModel):
    summary: str
    start_time: str
    end_time: str
    description: str = ""
    location: str = ""
    attendees: list[str] = []


@router.get("/today")
def get_today_agenda():
    """Obtiene la agenda de hoy."""
    try:
        cal = CalendarAutomation()
        return {"events": cal.get_today_agenda()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/upcoming")
def get_upcoming_events(days: int = 7):
    """Obtiene eventos próximos."""
    try:
        cal = CalendarAutomation()
        return {"events": cal.get_upcoming_events(days=days)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
def create_event(request: CreateEventRequest):
    """Crea un evento nuevo."""
    try:
        cal = CalendarAutomation()
        return cal.create_event(
            summary=request.summary,
            start_time=request.start_time,
            end_time=request.end_time,
            description=request.description,
            location=request.location,
            attendees=request.attendees,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{event_id}")
def cancel_event(event_id: str):
    """Cancela un evento."""
    try:
        cal = CalendarAutomation()
        return cal.cancel_event(event_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
