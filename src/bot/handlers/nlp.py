# src/bot/handlers/nlp.py
"""
NLP handler for THDORA — v3 with intent_parser integration.

Processes natural language messages and dispatches to appropriate handlers.
Uses Groq tool calling for complex queries via intent_parser.
"""

import logging
from datetime import date
from typing import Any, Dict

from telegram import Update
from telegram.ext import ContextTypes

from src.ai.intent_parser import parse_intent, IntentResult
from src.bot.api_client import ThdoraApiClient
from src.bot.keyboards import escape_md, _kb_start

logger = logging.getLogger(__name__)
api = ThdoraApiClient()


async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Main NLP handler. user_id always from update.effective_user.id."""
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    if not text:
        return

    await update.message.chat.send_action("typing")
    processing_msg = await update.message.reply_text("⏳ Procesando...")

    try:
        intent_result = await parse_intent(text, user_id=user_id)
        dispatch = {
            "nueva_cita": handle_nueva_cita,
            "borrar_cita": handle_borrar_cita,
            "editar_cita": handle_editar_cita,
            "log_habito": handle_log_habito,
            "borrar_habito": handle_borrar_habito,
            "consulta_nlp": handle_consulta_nlp,
        }
        handler = dispatch.get(intent_result.intent, handle_unknown)
        await handler(update, context, intent_result, user_id=user_id)
    except Exception as e:
        logger.error(f"Error in NLP handler: {e}", exc_info=True)
        await update.message.reply_text(
            escape_md("❌ Error interno\. Inténtalo de nuevo\."),
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )
    finally:
        try:
            await processing_msg.delete()
        except Exception:
            pass


async def handle_nueva_cita(update: Update, context: ContextTypes.DEFAULT_TYPE, intent_result: IntentResult, user_id: int) -> None:
    entities = intent_result.entities
    date_str = entities.get("date", date.today().isoformat())
    time = entities.get("time", "09:00")
    name = entities.get("name", "Cita")
    apt_type = entities.get("type", "otra")
    notes = entities.get("notes", "")

    conflict = await api.check_appointment_conflict(date_str, time, user_id=user_id)
    if conflict:
        await update.message.reply_text(
            f"⚠️ Las {escape_md(time)} del {escape_md(date_str)} ya tienes {escape_md(conflict.get('name', 'una cita'))}",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )
        return

    try:
        await api.create_appointment(date_str, time, name, apt_type, notes, user_id=user_id)
        await update.message.reply_text(
            f"✅ *{escape_md(name)}* añadida el {escape_md(date_str)} a las {escape_md(time)} ⏰",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        await update.message.reply_text(
            f"❌ No pude crear la cita: {escape_md(str(e))}",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )


async def handle_borrar_cita(update: Update, context: ContextTypes.DEFAULT_TYPE, intent_result: IntentResult, user_id: int) -> None:
    entities = intent_result.entities
    date_str = entities.get("date", date.today().isoformat())
    name = entities.get("name", "")

    try:
        appointments = await api.get_appointments(date_str, user_id=user_id)
        for apt in appointments:
            if name.lower() in apt["name"].lower():
                ok = await api.delete_appointment(date_str, apt["index"], user_id=user_id)
                if ok:
                    await update.message.reply_text(
                        f"✅ *{escape_md(apt['name'])}* eliminada del {escape_md(date_str)}",
                        parse_mode="MarkdownV2",
                        reply_markup=_kb_start()
                    )
                    return
        await update.message.reply_text(
            f"⚠️ No encontré la cita {escape_md(name)} en {escape_md(date_str)}",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )
    except Exception as e:
        logger.error(f"Error deleting appointment: {e}")
        await update.message.reply_text(
            f"❌ No pude borrar la cita: {escape_md(str(e))}",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )


async def handle_editar_cita(update: Update, context: ContextTypes.DEFAULT_TYPE, intent_result: IntentResult, user_id: int) -> None:
    entities = intent_result.entities
    date_str = entities.get("date", date.today().isoformat())
    time = entities.get("time")
    name = entities.get("name", "")

    if not time:
        await update.message.reply_text(
            "⏰ ¿A qué hora quieres mover la cita?",
            reply_markup=_kb_start()
        )
        return

    try:
        appointments = await api.get_appointments(date_str, user_id=user_id)
        for apt in appointments:
            if name.lower() in apt["name"].lower():
                updated = await api.update_appointment(date_str, apt["index"], time=time, user_id=user_id)
                if updated:
                    await update.message.reply_text(
                        f"✅ *{escape_md(apt['name'])}* movida a {escape_md(time)}",
                        parse_mode="MarkdownV2",
                        reply_markup=_kb_start()
                    )
                    return
        await update.message.reply_text(
            f"⚠️ No encontré la cita {escape_md(name)} en {escape_md(date_str)}",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )
    except Exception as e:
        logger.error(f"Error updating appointment: {e}")
        await update.message.reply_text(
            f"❌ No pude editar la cita: {escape_md(str(e))}",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )


async def handle_log_habito(update: Update, context: ContextTypes.DEFAULT_TYPE, intent_result: IntentResult, user_id: int) -> None:
    entities = intent_result.entities
    date_str = entities.get("date", date.today().isoformat())
    habit = entities.get("habit", "")
    value = entities.get("value", "")

    if not habit:
        await update.message.reply_text(
            "❓ No he entendido el hábito\. Ejemplo: dormí 8 horas",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )
        return

    try:
        await api.log_habit(date_str, habit, value, user_id=user_id)
        await update.message.reply_text(
            f"✅ *{escape_md(habit)}*: {escape_md(value)} registrado",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )
    except Exception as e:
        logger.error(f"Error logging habit: {e}")
        await update.message.reply_text(
            f"❌ No pude registrar el hábito: {escape_md(str(e))}",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )


async def handle_borrar_habito(update: Update, context: ContextTypes.DEFAULT_TYPE, intent_result: IntentResult, user_id: int) -> None:
    entities = intent_result.entities
    date_str = entities.get("date", date.today().isoformat())
    habit = entities.get("habit", "")

    try:
        ok = await api.delete_habit(date_str, habit, user_id=user_id)
        if ok:
            await update.message.reply_text(
                f"✅ *{escape_md(habit)}* eliminado del {escape_md(date_str)}",
                parse_mode="MarkdownV2",
                reply_markup=_kb_start()
            )
        else:
            await update.message.reply_text(
                f"⚠️ No encontré el hábito {escape_md(habit)} en {escape_md(date_str)}",
                parse_mode="MarkdownV2",
                reply_markup=_kb_start()
            )
    except Exception as e:
        logger.error(f"Error deleting habit: {e}")
        await update.message.reply_text(
            f"❌ No pude borrar el hábito: {escape_md(str(e))}",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )


async def handle_consulta_nlp(update: Update, context: ContextTypes.DEFAULT_TYPE, intent_result: IntentResult, user_id: int) -> None:
    """Handle consulta_nlp — delegates to groq_router for full Toki mode."""
    try:
        from src.bot.groq_router import route
        result = await route(
            text=update.message.text or "",
            user_data=context.user_data if context else {},
            api_context={},
            username=update.effective_user.first_name or "Usuario",
            user_id=user_id,
        )
        reply = result.get("reply", "No he entendido la consulta")
        await update.message.reply_text(
            escape_md(reply),
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )
    except Exception as e:
        logger.error(f"Error in consulta_nlp: {e}")
        await update.message.reply_text(
            "🤔 No he entendido\. Usa /help para ver comandos disponibles\.",
            parse_mode="MarkdownV2",
            reply_markup=_kb_start()
        )


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE, intent_result: IntentResult, user_id: int) -> None:
    """Handle desconocido intent."""
    await update.message.reply_text(
        "🤔 No he entendido\. Usa /help para ver los comandos disponibles\.",
        parse_mode="MarkdownV2",
        reply_markup=_kb_start()
    )
