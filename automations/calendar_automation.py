"""Automatización de Google Calendar: agenda, crear/cancelar eventos."""

from datetime import datetime, timedelta
from config.google_auth import build_service


class CalendarAutomation:
    def __init__(self):
        self.service = build_service("calendar", "v3")

    def get_today_agenda(self) -> list[dict]:
        """Obtiene los eventos de hoy."""
        now = datetime.utcnow()
        start = now.replace(hour=0, minute=0, second=0).isoformat() + "Z"
        end = now.replace(hour=23, minute=59, second=59).isoformat() + "Z"

        events_result = self.service.events().list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
        return [
            {
                "id": event["id"],
                "summary": event.get("summary", "Sin título"),
                "start": event["start"].get("dateTime", event["start"].get("date")),
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "location": event.get("location", ""),
                "description": event.get("description", ""),
                "attendees": [a["email"] for a in event.get("attendees", [])],
            }
            for event in events
        ]

    def get_upcoming_events(self, days: int = 7, max_results: int = 20) -> list[dict]:
        """Obtiene los eventos de los próximos N días."""
        now = datetime.utcnow()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(days=days)).isoformat() + "Z"

        events_result = self.service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
        return [
            {
                "id": event["id"],
                "summary": event.get("summary", "Sin título"),
                "start": event["start"].get("dateTime", event["start"].get("date")),
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "location": event.get("location", ""),
            }
            for event in events
        ]

    def create_event(
        self, summary: str, start_time: str, end_time: str,
        description: str = "", location: str = "", attendees: list[str] = None,
    ) -> dict:
        """Crea un evento nuevo en el calendario."""
        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "America/Bogota"},
            "end": {"dateTime": end_time, "timeZone": "America/Bogota"},
        }

        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        result = self.service.events().insert(
            calendarId="primary", body=event
        ).execute()

        return {
            "id": result["id"],
            "summary": result["summary"],
            "link": result.get("htmlLink", ""),
            "status": "created",
        }

    def cancel_event(self, event_id: str) -> dict:
        """Cancela (elimina) un evento."""
        self.service.events().delete(
            calendarId="primary", eventId=event_id
        ).execute()
        return {"id": event_id, "status": "cancelled"}
