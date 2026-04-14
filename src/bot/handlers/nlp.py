"""
Handler de texto libre — modo Toki.

Flujo completo:
    1. Envía ⏳ Procesando... (feedback inmediato mientras trabaja Groq)
    2. Consulta contexto real de la API:
       — citas de hoy y mañana
       — hábitos de hoy
       Si la API falla, el contexto queda vacío y el bot sigue funcionando.
    3. Llama a groq_router.route() con el texto + contexto
    4. Según el intent:
       nueva_cita  → crea la cita en la API (con fix hora 00:00)
       log_habito  → registra el hábito en la API
       consulta    → responde con datos reales de la agenda
       chat        → respuesta conversacional con contexto
       desconocido → muestra el menú principal del bot (NO texto suelto)

Diseño Toki:
    La IA actua solo como router de intención + extractor de slots.
    Cuando no entiende, devuelve siempre la interfaz del bot (botones),
    no una respuesta de texto inventada.
    El contexto real (agenda + hábitos) se inyecta en el prompt antes
    de llamar a Groq, para respuestas tipo ¿qué tengo mañana?
"""

import logging
from datetime import date, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.api_client import ThdoraApiClient
from src.bot.groq_router import route
from src.bot.keyboards import _kb_start

logger = logging.getLogger(__name__)
api    = ThdoraApiClient()

_MSG_MENU = (
    "🤔 No he entendido bien lo que quieres hacer.\n"
    "Usa los botones o escíbeme algo como:\n"
    "  • _\"mañana dentista a las 5\"_\n"
    "  • _\"dormí 7 horas\"_"
)

_MSG_HORA_CONFIRM = (
    "⏰ No he detectado la hora. ¿A qué hora es la cita _{name}_?\n"
    "Escíbeme la hora (ej: _17:00_) o usa /nueva para el flujo guiado."
)


async def _get_api_context(today: str, tomorrow: str) -> dict:
    """
    Obtiene el contexto real de la API para inyectar en el prompt de Groq.
    Hace las 3 llamadas en paralelo con gather. Si alguna falla, devuelve
    lo que haya podido obtener (degradación elegante).
    """
    import asyncio

    async def _safe(coro):
        try:
            return await coro
        except Exception:
            return None

    citas, citas_man, habitos = await asyncio.gather(
        _safe(api.get_appointments(today)),
        _safe(api.get_appointments(tomorrow)),
        _safe(api.get_habits(today)),
    )
    return {
        "citas":        citas        or [],
        "citas_manana": citas_man    or [],
        "habitos":      habitos      or {},
    }


async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    if not text:
        return

    today    = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # 1. Feedback inmediato
    processing_msg = await update.message.reply_text("⏳ Procesando...")

    # 2. Contexto real de la API (paralelo)
    api_context = await _get_api_context(today, tomorrow)

    # 3. Router NLP con contexto
    result = await route(
        text=text,
        user_data=context.user_data,
        api_context=api_context,
    )

    # Borrar ⏳ Procesando...
    try:
        await processing_msg.delete()
    except Exception:
        pass

    intent    = result["intent"]
    data      = result["data"]
    reply     = result["reply"]
    show_menu = result.get("show_menu", False)

    # ── intent desconocido → menú del bot ─────────────────────────────
    if show_menu:
        await update.message.reply_text(
            _MSG_MENU,
            parse_mode="Markdown",
            reply_markup=_kb_start(),
        )
        return

    # ── reply sola (fallo extraccion, chat, consulta) ───────────────────
    if reply and not data:
        await update.message.reply_text(reply, parse_mode="Markdown")
        return

    # ── nueva_cita ────────────────────────────────────────────────────
    if intent == "nueva_cita" and data:
        cita_date = data.get("date", today)
        cita_time = data.get("time", "09:00")
        cita_name = data.get("name", "Cita")
        cita_type = data.get("type", "otro")
        cita_notes = data.get("notes", "")

        # Fix hora 00:00: pedir confirmación en vez de crear a medianoche
        if cita_time == "00:00":
            await update.message.reply_text(
                _MSG_HORA_CONFIRM.format(name=cita_name),
                parse_mode="Markdown",
            )
            return

        # Conflicto de hora
        conflict = await api.check_appointment_conflict(cita_date, cita_time)
        if conflict:
            await update.message.reply_text(
                f"⚠️ Ya tienes *{conflict.get('name', 'una cita')}* "
                f"el {cita_date} a las {cita_time}.\n"
                f"Elige otra hora o usa /nueva para el flujo guiado.",
                parse_mode="Markdown",
            )
            return

        try:
            await api.create_appointment(
                date_str=cita_date,
                time=cita_time,
                name=cita_name,
                apt_type=cita_type,
                notes=cita_notes,
            )
            await update.message.reply_text(
                f"✅ *{cita_name}* añadida el {cita_date} a las {cita_time} \u231f",
                parse_mode="Markdown",
                reply_markup=_kb_start(),
            )
        except Exception as e:
            logger.error("Error creando cita desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude crear la cita ({e}).\nPrueba con /nueva.",
                reply_markup=_kb_start(),
            )
        return

    # ── log_habito ──────────────────────────────────────────────────────
    if intent == "log_habito" and data:
        hab_date  = data.get("date", today)
        hab_name  = data.get("habit", "hábito")
        hab_value = data.get("value", "")

        try:
            await api.log_habit(
                date_str=hab_date,
                habit=hab_name,
                value=hab_value,
            )
            await update.message.reply_text(
                f"✅ *{hab_name}*: {hab_value} — registrado",
                parse_mode="Markdown",
                reply_markup=_kb_start(),
            )
        except Exception as e:
            logger.error("Error registrando hábito desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude registrar el hábito ({e}).\nPrueba con /habito.",
                reply_markup=_kb_start(),
            )
        return
