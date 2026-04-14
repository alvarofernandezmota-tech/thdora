"""
Handler de lenguaje natural (NLP) para THDORA.

Actúa cuando el usuario escribe texto libre fuera de cualquier
ConversationHandler activo y NO está acumulando un hábito.

Flujo:
    texto libre → groq_router.route() → intent
        nueva_cita  → api.create_appointment() → confirmación
        log_habito  → api.log_habit()           → confirmación
        chat/otros  → respuesta conversacional
"""

import logging
from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.api_client import ThdoraApiClient
from src.bot.groq_router import route

logger = logging.getLogger(__name__)
api    = ThdoraApiClient()

_TIPOS_ES = {
    "medica":   "🏥 Médica",
    "personal": "👤 Personal",
    "trabajo":  "💼 Trabajo",
    "otro":     "📌 Otro",
}


async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler principal de texto libre con NLP.
    Se llama desde _route_free_text() en main.py.
    """
    text     = update.message.text.strip()
    user_data = context.user_data

    # Indicador de escritura mientras procesa
    await update.message.chat.send_action("typing")

    result = await route(text, user_data)
    intent = result["intent"]
    data   = result["data"]
    reply  = result["reply"]

    # ── Crear cita ────────────────────────────────────────────────────
    if intent == "nueva_cita" and data:
        await _handle_nueva_cita(update, data)
        return

    # ── Registrar hábito ──────────────────────────────────────────────
    if intent == "log_habito" and data:
        await _handle_log_habito(update, data)
        return

    # ── Chat / consulta / desconocido ────────────────────────────────
    if reply:
        await update.message.reply_text(reply)
        return

    await update.message.reply_text(
        "🤔 No he entendido bien. Puedes usar /nueva para una cita o /habito para un hábito."
    )


async def _handle_nueva_cita(update: Update, data: dict) -> None:
    """Crea la cita en la API y confirma al usuario."""
    try:
        date_str = data.get("date") or date.today().isoformat()
        time_str = data.get("time", "09:00")
        name     = data.get("name", "Cita")
        apt_type = data.get("type", "otro")
        notes    = data.get("notes", "")

        # Comprobar conflicto de hora
        conflict = await api.check_appointment_conflict(date_str, time_str)
        if conflict:
            await update.message.reply_text(
                f"⚠️ Ya tienes *{conflict['name']}* a las *{time_str}* el {date_str}.\n"
                f"Usa /nueva para elegir otra hora.",
                parse_mode="Markdown",
            )
            return

        await api.create_appointment(
            date_str=date_str,
            time=time_str,
            name=name,
            apt_type=apt_type,
            notes=notes,
        )

        tipo_label = _TIPOS_ES.get(apt_type, "📌 Otro")
        # Formatear fecha legible
        from datetime import datetime
        fecha_bonita = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")

        await update.message.reply_text(
            f"✅ *{name}* el *{fecha_bonita}* a las *{time_str}*\n"
            f"Tipo: {tipo_label}",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error("Error creando cita desde NLP: %s", e)
        await update.message.reply_text(
            "⚠️ No pude crear la cita. Inténtalo con /nueva."
        )


async def _handle_log_habito(update: Update, data: dict) -> None:
    """Registra el hábito en la API y confirma al usuario."""
    try:
        date_str = data.get("date") or date.today().isoformat()
        habit    = data.get("habit", "")
        value    = data.get("value", "")

        if not habit or not value:
            await update.message.reply_text(
                "🤔 No entendí bien el hábito. Puedes usar /habito para registrarlo."
            )
            return

        await api.log_habit(date_str=date_str, habit=habit, value=value)

        from datetime import datetime
        fecha_bonita = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")

        await update.message.reply_text(
            f"✅ *{habit}*: {value} — {fecha_bonita}",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error("Error registrando hábito desde NLP: %s", e)
        await update.message.reply_text(
            "⚠️ No pude registrar el hábito. Inténtalo con /habito."
        )
