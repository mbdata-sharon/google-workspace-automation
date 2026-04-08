"""Bot de Telegram para controlar Google Workspace con lenguaje natural."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters,
)

from automations.gmail_automation import GmailAutomation
from automations.calendar_automation import CalendarAutomation
from automations.drive_automation import DriveAutomation
from automations.ai_assistant import AIAssistant
from config.settings import TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache temporal para confirmaciones pendientes
pending_actions = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Bienvenida."""
    await update.message.reply_text(
        "Hola! Soy tu asistente de Google Workspace.\n\n"
        "Comandos disponibles:\n"
        "/inbox - Ver emails no leídos\n"
        "/triage - Clasificar emails por prioridad\n"
        "/resumen - Resumen inteligente de emails\n"
        "/agenda - Agenda de hoy\n"
        "/semana - Eventos de la semana\n"
        "/archivos - Archivos recientes en Drive\n"
        "/buscar [texto] - Buscar en Drive\n"
        "/responder - Responder un email con IA\n"
        "/enviar - Enviar un email nuevo\n"
        "/evento - Crear un evento\n\n"
        "Tambien puedes escribirme en lenguaje natural!"
    )


async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /inbox - Emails no leídos."""
    await update.message.reply_text("Revisando tu inbox...")
    try:
        gmail = GmailAutomation()
        emails = gmail.get_unread_emails(max_results=5)

        if not emails:
            await update.message.reply_text("No tienes emails no leídos!")
            return

        for email in emails:
            keyboard = [
                [
                    InlineKeyboardButton("Responder", callback_data=f"reply_{email['id']}_{email.get('thread_id', '')}"),
                    InlineKeyboardButton("Ver completo", callback_data=f"read_{email['id']}"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"*De:* {email['from']}\n"
                f"*Asunto:* {email['subject']}\n"
                f"*Fecha:* {email['date']}\n"
                f"_{email['snippet'][:150]}_",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def triage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /triage - Clasificar emails."""
    await update.message.reply_text("Clasificando tu inbox...")
    try:
        gmail = GmailAutomation()
        result = gmail.triage_inbox()

        msg = "*TRIAGE DE INBOX*\n\n"

        if result["urgent"]:
            msg += "URGENTE:\n"
            for e in result["urgent"]:
                msg += f"  - {e['subject']} (de: {e['from']})\n"

        if result["important"]:
            msg += "\nIMPORTANTE:\n"
            for e in result["important"]:
                msg += f"  - {e['subject']} (de: {e['from']})\n"

        if result["low"]:
            msg += f"\nBAJA PRIORIDAD: {len(result['low'])} emails\n"

        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /resumen - Resumen con IA."""
    await update.message.reply_text("Generando resumen con IA...")
    try:
        gmail = GmailAutomation()
        ai = AIAssistant()
        emails = gmail.get_unread_emails(max_results=15)
        summary = ai.summarize_emails(emails)

        await update.message.reply_text(
            f"*RESUMEN DE INBOX* ({len(emails)} no leídos)\n\n{summary}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def agenda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /agenda - Eventos de hoy."""
    try:
        cal = CalendarAutomation()
        events = cal.get_today_agenda()

        if not events:
            await update.message.reply_text("No tienes eventos para hoy!")
            return

        msg = "*AGENDA DE HOY*\n\n"
        for event in events:
            start = event["start"]
            if "T" in start:
                start = start.split("T")[1][:5]
            msg += f"  *{start}* - {event['summary']}\n"
            if event["location"]:
                msg += f"    Lugar: {event['location']}\n"

        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /semana - Eventos de la semana."""
    try:
        cal = CalendarAutomation()
        events = cal.get_upcoming_events(days=7)

        if not events:
            await update.message.reply_text("No tienes eventos esta semana!")
            return

        msg = "*EVENTOS DE LA SEMANA*\n\n"
        current_date = ""
        for event in events:
            date = event["start"].split("T")[0] if "T" in event["start"] else event["start"]
            if date != current_date:
                current_date = date
                msg += f"\n*{date}*\n"
            time = event["start"].split("T")[1][:5] if "T" in event["start"] else "Todo el día"
            msg += f"  {time} - {event['summary']}\n"

        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def archivos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /archivos - Archivos recientes."""
    try:
        drive = DriveAutomation()
        files = drive.list_recent_files(max_results=10)

        msg = "*ARCHIVOS RECIENTES*\n\n"
        for f in files:
            msg += f"  [{f['name']}]({f['link']})\n"
            msg += f"    Modificado: {f['modified'][:10]}\n"

        await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /buscar [query] - Buscar en Drive."""
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("Uso: /buscar nombre del archivo")
        return

    try:
        drive = DriveAutomation()
        files = drive.search_files(query)

        if not files:
            await update.message.reply_text(f"No encontré archivos con: '{query}'")
            return

        msg = f"*Resultados para '{query}':*\n\n"
        for f in files:
            msg += f"  [{f['name']}]({f['link']})\n"

        await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def responder_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /responder - Responder email con IA."""
    await update.message.reply_text(
        "Primero te muestro tus emails recientes. "
        "Haz clic en 'Responder' en el que quieras contestar."
    )
    await inbox(update, context)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los botones inline."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("read_"):
        message_id = data.replace("read_", "")
        try:
            gmail = GmailAutomation()
            body = gmail.get_email_body(message_id)
            await query.message.reply_text(
                f"*EMAIL COMPLETO:*\n\n{body[:3000]}",
                parse_mode="Markdown",
            )
        except Exception as e:
            await query.message.reply_text(f"Error: {e}")

    elif data.startswith("reply_"):
        parts = data.split("_")
        message_id = parts[1]
        thread_id = parts[2] if len(parts) > 2 else ""

        pending_actions[query.from_user.id] = {
            "action": "reply",
            "message_id": message_id,
            "thread_id": thread_id,
        }

        await query.message.reply_text(
            "Escribe tu instruccion para la respuesta.\n\n"
            "Ejemplo: _'dile cordialmente que no puedo asistir a la reunion "
            "por compromisos laborales'_",
            parse_mode="Markdown",
        )

    elif data.startswith("confirm_send_"):
        user_id = query.from_user.id
        if user_id in pending_actions and "ai_reply" in pending_actions[user_id]:
            action = pending_actions[user_id]
            try:
                gmail = GmailAutomation()
                result = gmail.reply_to_email(
                    action["message_id"], action["thread_id"], action["ai_reply"]
                )
                await query.message.reply_text("Email enviado exitosamente!")
                del pending_actions[user_id]
            except Exception as e:
                await query.message.reply_text(f"Error al enviar: {e}")

    elif data == "cancel_send":
        user_id = query.from_user.id
        if user_id in pending_actions:
            del pending_actions[user_id]
        await query.message.reply_text("Envio cancelado.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto (instrucciones en lenguaje natural)."""
    user_id = update.message.from_user.id
    text = update.message.text

    # Si hay una accion pendiente de reply
    if user_id in pending_actions and pending_actions[user_id]["action"] == "reply":
        action = pending_actions[user_id]
        await update.message.reply_text("Generando respuesta con IA...")

        try:
            gmail = GmailAutomation()
            ai = AIAssistant()

            original_body = gmail.get_email_body(action["message_id"])
            ai_reply = ai.generate_email_reply(original_body, text)

            action["ai_reply"] = ai_reply

            keyboard = [
                [
                    InlineKeyboardButton("Enviar", callback_data="confirm_send_"),
                    InlineKeyboardButton("Cancelar", callback_data="cancel_send"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"*BORRADOR DE RESPUESTA:*\n\n{ai_reply}\n\n"
                "Quieres enviar esta respuesta?",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
        return

    # Mensaje genérico
    await update.message.reply_text(
        "No entendi tu mensaje. Usa /start para ver los comandos disponibles."
    )


def main():
    """Inicia el bot de Telegram."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("inbox", inbox))
    app.add_handler(CommandHandler("triage", triage))
    app.add_handler(CommandHandler("resumen", resumen))
    app.add_handler(CommandHandler("agenda", agenda))
    app.add_handler(CommandHandler("semana", semana))
    app.add_handler(CommandHandler("archivos", archivos))
    app.add_handler(CommandHandler("buscar", buscar))
    app.add_handler(CommandHandler("responder", responder_email))

    # Callbacks (botones)
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot de Telegram iniciado!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
