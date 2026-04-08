"""Automatización de Gmail: leer, buscar, responder, enviar, triage."""

import base64
from email.mime.text import MIMEText
from config.google_auth import build_service


class GmailAutomation:
    def __init__(self):
        self.service = build_service("gmail", "v1")

    def get_unread_emails(self, max_results: int = 10) -> list[dict]:
        """Obtiene los emails no leídos."""
        results = self.service.users().messages().list(
            userId="me", q="is:unread", maxResults=max_results
        ).execute()

        messages = results.get("messages", [])
        emails = []
        for msg in messages:
            detail = self.service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()

            headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
            emails.append({
                "id": msg["id"],
                "thread_id": detail["threadId"],
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": detail.get("snippet", ""),
            })

        return emails

    def get_email_body(self, message_id: str) -> str:
        """Obtiene el cuerpo completo de un email."""
        message = self.service.users().messages().get(
            userId="me", id=message_id, format="full"
        ).execute()

        parts = message.get("payload", {}).get("parts", [])
        body = ""

        if parts:
            for part in parts:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    body = base64.urlsafe_b64decode(data).decode("utf-8")
                    break
        else:
            data = message["payload"]["body"].get("data", "")
            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8")

        return body

    def send_email(self, to: str, subject: str, body: str) -> dict:
        """Envía un email nuevo."""
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = self.service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()

        return {"id": result["id"], "status": "sent"}

    def reply_to_email(self, message_id: str, thread_id: str, body: str) -> dict:
        """Responde a un email existente."""
        original = self.service.users().messages().get(
            userId="me", id=message_id, format="metadata",
            metadataHeaders=["From", "Subject"]
        ).execute()

        headers = {h["name"]: h["value"] for h in original["payload"]["headers"]}
        to = headers.get("From", "")
        subject = headers.get("Subject", "")

        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        message["In-Reply-To"] = message_id
        message["References"] = message_id

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = self.service.users().messages().send(
            userId="me", body={"raw": raw, "threadId": thread_id}
        ).execute()

        return {"id": result["id"], "thread_id": thread_id, "status": "replied"}

    def search_emails(self, query: str, max_results: int = 10) -> list[dict]:
        """Busca emails con una query de Gmail."""
        results = self.service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        ).execute()

        messages = results.get("messages", [])
        emails = []
        for msg in messages:
            detail = self.service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()

            headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
            emails.append({
                "id": msg["id"],
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": detail.get("snippet", ""),
            })

        return emails

    def triage_inbox(self) -> dict:
        """Clasifica los emails no leídos por prioridad."""
        emails = self.get_unread_emails(max_results=20)

        triage = {"urgent": [], "important": [], "low": []}

        for email in emails:
            from_addr = email["from"].lower()
            subject = email["subject"].lower()

            if any(w in subject for w in ["urgente", "urgent", "asap", "inmediato"]):
                triage["urgent"].append(email)
            elif any(w in subject for w in ["reunión", "meeting", "factura", "pago", "colegio"]):
                triage["important"].append(email)
            else:
                triage["low"].append(email)

        return triage
