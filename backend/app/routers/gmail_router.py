"""API endpoints para Gmail."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from automations.gmail_automation import GmailAutomation
from automations.ai_assistant import AIAssistant

router = APIRouter()


class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str


class ReplyEmailRequest(BaseModel):
    message_id: str
    thread_id: str
    instruction: str
    tone: str = "cordial"


class SearchRequest(BaseModel):
    query: str
    max_results: int = 10


@router.get("/unread")
def get_unread_emails():
    """Obtiene emails no leídos."""
    try:
        gmail = GmailAutomation()
        return {"emails": gmail.get_unread_emails()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/triage")
def triage_inbox():
    """Clasifica emails por prioridad."""
    try:
        gmail = GmailAutomation()
        return gmail.triage_inbox()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
def send_email(request: SendEmailRequest):
    """Envía un email."""
    try:
        gmail = GmailAutomation()
        return gmail.send_email(request.to, request.subject, request.body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reply")
def reply_to_email(request: ReplyEmailRequest):
    """Responde a un email con IA."""
    try:
        gmail = GmailAutomation()
        ai = AIAssistant()

        original_body = gmail.get_email_body(request.message_id)
        ai_reply = ai.generate_email_reply(
            original_body, request.instruction, request.tone
        )

        return {
            "draft": ai_reply,
            "message_id": request.message_id,
            "thread_id": request.thread_id,
            "status": "draft_ready",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reply/confirm")
def confirm_reply(request: ReplyEmailRequest):
    """Confirma y envía la respuesta generada por IA."""
    try:
        gmail = GmailAutomation()
        ai = AIAssistant()

        original_body = gmail.get_email_body(request.message_id)
        ai_reply = ai.generate_email_reply(
            original_body, request.instruction, request.tone
        )

        result = gmail.reply_to_email(
            request.message_id, request.thread_id, ai_reply
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
def search_emails(request: SearchRequest):
    """Busca emails."""
    try:
        gmail = GmailAutomation()
        return {"emails": gmail.search_emails(request.query, request.max_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
def email_summary():
    """Resumen inteligente de emails no leídos."""
    try:
        gmail = GmailAutomation()
        ai = AIAssistant()
        emails = gmail.get_unread_emails(max_results=15)
        summary = ai.summarize_emails(emails)
        return {"summary": summary, "total_unread": len(emails)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
