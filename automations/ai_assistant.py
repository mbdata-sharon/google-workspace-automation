"""Asistente IA con OpenRouter para generar respuestas inteligentes (gratis)."""

import httpx
from config.settings import OPENROUTER_API_KEY

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


class AIAssistant:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

    def _chat(self, prompt: str) -> str:
        """Envía un prompt al modelo y retorna la respuesta."""
        response = httpx.post(
            OPENROUTER_URL,
            headers=self.headers,
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024,
            },
            timeout=60,
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def generate_email_reply(
        self, original_email: str, user_instruction: str, tone: str = "cordial"
    ) -> str:
        """Genera una respuesta de email basada en instrucciones del usuario."""
        return self._chat(
            f"""Genera una respuesta de email en español.

TONO: {tone}
EMAIL ORIGINAL:
{original_email}

INSTRUCCIÓN DEL USUARIO: {user_instruction}

Escribe SOLO el cuerpo del email de respuesta, sin "Asunto:" ni encabezados.
Debe ser profesional, {tone} y directo."""
        )

    def summarize_emails(self, emails: list[dict]) -> str:
        """Resume una lista de emails no leídos."""
        email_text = "\n\n".join(
            f"De: {e['from']}\nAsunto: {e['subject']}\nResumen: {e['snippet']}"
            for e in emails
        )

        return self._chat(
            f"""Resume estos emails no leídos en español.
Agrúpalos por prioridad (urgente, importante, informativo).
Sé conciso, máximo 2 líneas por email.

EMAILS:
{email_text}"""
        )

    def generate_standup_report(
        self, emails_summary: str, calendar_events: str, tasks: str
    ) -> str:
        """Genera un reporte de standup diario."""
        return self._chat(
            f"""Genera un reporte de standup diario en español basado en:

EMAILS DE HOY:
{emails_summary}

EVENTOS DEL CALENDARIO:
{calendar_events}

TAREAS:
{tasks}

Formato:
- Que hice ayer (inferir de emails/eventos pasados)
- Que haré hoy (basado en calendario y tareas)
- Bloqueantes (si los hay)"""
        )
