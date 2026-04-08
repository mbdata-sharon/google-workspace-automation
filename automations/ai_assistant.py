"""Asistente IA con Claude para generar respuestas inteligentes."""

import anthropic
from config.settings import ANTHROPIC_API_KEY


class AIAssistant:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate_email_reply(
        self, original_email: str, user_instruction: str, tone: str = "cordial"
    ) -> str:
        """Genera una respuesta de email basada en instrucciones del usuario."""
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Genera una respuesta de email en español.

TONO: {tone}
EMAIL ORIGINAL:
{original_email}

INSTRUCCIÓN DEL USUARIO: {user_instruction}

Escribe SOLO el cuerpo del email de respuesta, sin "Asunto:" ni encabezados.
Debe ser profesional, {tone} y directo.""",
                }
            ],
        )

        return message.content[0].text

    def summarize_emails(self, emails: list[dict]) -> str:
        """Resume una lista de emails no leídos."""
        email_text = "\n\n".join(
            f"De: {e['from']}\nAsunto: {e['subject']}\nResumen: {e['snippet']}"
            for e in emails
        )

        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Resume estos emails no leídos en español.
Agrúpalos por prioridad (urgente, importante, informativo).
Sé conciso, máximo 2 líneas por email.

EMAILS:
{email_text}""",
                }
            ],
        )

        return message.content[0].text

    def generate_standup_report(
        self, emails_summary: str, calendar_events: str, tasks: str
    ) -> str:
        """Genera un reporte de standup diario."""
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Genera un reporte de standup diario en español basado en:

EMAILS DE HOY:
{emails_summary}

EVENTOS DEL CALENDARIO:
{calendar_events}

TAREAS:
{tasks}

Formato:
- Que hice ayer (inferir de emails/eventos pasados)
- Que haré hoy (basado en calendario y tareas)
- Bloqueantes (si los hay)""",
                }
            ],
        )

        return message.content[0].text
