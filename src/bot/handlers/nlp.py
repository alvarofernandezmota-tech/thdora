# src/bot/handlers/nlp.py
import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.api_client import ThdoraApiClient
from src.bot.keyboards import _kb_start

logger = logging.getLogger(__name__)
api = ThdoraApiClient()

async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    if not text:
        return

    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    await update.message.chat.send_action("typing")
    processing_msg = await update.message.reply_text("⏳ Procesando...")

    try:
        result = await _process_nlp(text, today, tomorrow, user_id)
        await processing_msg.delete()
        await _handle_nlp_result(update, context, result, today, user_id)
    except Exception as e:
        logger.error(f"Error en NLP: {e}")
        try:
            await processing_msg.delete()
        except Exception:
            pass
        await update.message.reply_text("❌ Error al procesar", reply_markup=_kb_start())

async def _process_nlp(text: str, today: str, tomorrow: str, user_id: int) -> Dict[str, Any]:
    text_lower = text.lower()

    if any(w in text_lower for w in ["cancela", "borra", "elimina"]):
        if "cita" in text_lower:
            return await _process_borrar_cita(text, today, user_id)
        elif any(w in text_lower for w in ["hábito", "habito"]):
            return await _process_borrar_habito(text, today, user_id)
    elif any(w in text_lower for w in ["nueva", "añade", "agrega"]):
        if "cita" in text_lower:
            return await _process_nueva_cita(text, today, user_id)
        elif any(w in text_lower for w in ["hábito", "habito"]):
            return await _process_log_habito(text, today, user_id)
    elif any(w in text_lower for w in ["mueve", "cambia", "edita"]):
        return await _process_editar_cita(text, today, user_id)
    elif any(w in text_lower for w in ["dorm", "comí", "comi", "beb", "hice"]):
        return await _process_log_habito(text, today, user_id)

    return {"intent": "unknown", "reply": "🤔 No he entendido. Usa /help para ver comandos."}

async def _process_nueva_cita(text: str, today: str, user_id: int) -> Dict[str, Any]:
    time_match = _extract_time(text)
    if not time_match:
        return {"intent": "nueva_cita", "reply": "⏰ No he detectado la hora. Ejemplo: mañana dentista a las 10"}

    date_str = _extract_date(text, today)
    name, apt_type = _extract_name_type(text)

    conflict = await api.check_appointment_conflict(date_str, time_match, user_id=user_id)
    if conflict:
        return {"intent": "conflict", "reply": f"⚠️ Las {time_match} del {date_str} ya tienes {conflict['name']}"}

    await api.create_appointment(date_str, time_match, name, apt_type, "", user_id=user_id)
    return {"intent": "nueva_cita", "reply": f"✅ *{name}* añadida el {date_str} a las {time_match} ⏰"}

async def _process_borrar_cita(text: str, today: str, user_id: int) -> Dict[str, Any]:
    date_str = _extract_date(text, today)
    appointments = await api.get_appointments(date_str, user_id=user_id)
    name = _extract_name(text)
    for apt in appointments:
        if name in apt["name"].lower() or name in apt["type"].lower():
            ok = await api.delete_appointment(date_str, apt["index"], user_id=user_id)
            if ok:
                return {"intent": "borrar_cita", "reply": f"✅ *{apt['name']}* eliminada del {date_str}"}
            break
    return {"intent": "borrar_cita", "reply": f"⚠️ No encontré la cita en {date_str}"}

async def _process_editar_cita(text: str, today: str, user_id: int) -> Dict[str, Any]:
    date_str = _extract_date(text, today)
    time_match = _extract_time(text)
    name = _extract_name(text)
    if not time_match:
        return {"intent": "editar_cita", "reply": "⏰ ¿A qué hora quieres moverla?"}
    appointments = await api.get_appointments(date_str, user_id=user_id)
    for apt in appointments:
        if name in apt["name"].lower():
            ok = await api.update_appointment(date_str, apt["index"], time=time_match, user_id=user_id)
            if ok:
                return {"intent": "editar_cita", "reply": f"✅ *{apt['name']}* movida a {time_match}"}
            break
    return {"intent": "editar_cita", "reply": f"⚠️ No encontré la cita en {date_str}"}

async def _process_log_habito(text: str, today: str, user_id: int) -> Dict[str, Any]:
    habit, value = _extract_habit_value(text)
    if not habit:
        return {"intent": "log_habito", "reply": "❓ No he entendido el hábito. Ejemplo: dormí 8 horas"}
    await api.log_habit(today, habit, value, user_id=user_id)
    return {"intent": "log_habito", "reply": f"✅ *{habit}*: {value} registrado"}

async def _process_borrar_habito(text: str, today: str, user_id: int) -> Dict[str, Any]:
    habit = _extract_name(text)
    if not habit:
        return {"intent": "borrar_habito", "reply": "❓ No he entendido el hábito a borrar"}
    ok = await api.delete_habit(today, habit, user_id=user_id)
    if ok:
        return {"intent": "borrar_habito", "reply": f"✅ *{habit}* eliminado de hoy"}
    return {"intent": "borrar_habito", "reply": f"⚠️ No encontré el hábito *{habit}* hoy"}

async def _handle_nlp_result(update: Update, context: ContextTypes.DEFAULT_TYPE, result: Dict[str, Any], today: str, user_id: int) -> None:
    reply = result.get("reply", "")
    if reply:
        await update.message.reply_text(reply, parse_mode="Markdown", reply_markup=_kb_start())
    else:
        await update.message.reply_text("🤔 No he entendido. Usa /help", parse_mode="Markdown", reply_markup=_kb_start())

def _extract_time(text: str) -> Optional[str]:
    import re
    match = re.search(r"(\d{1,2}:\d{2})", text)
    return match.group(1) if match else None

def _extract_date(text: str, today: str) -> str:
    text_lower = text.lower()
    if "mañana" in text_lower:
        return (date.today() + timedelta(days=1)).isoformat()
    elif "ayer" in text_lower:
        return (date.today() - timedelta(days=1)).isoformat()
    return today

def _extract_name(text: str) -> str:
    words = text.lower().split()
    for word in ["cita", "reunión", "reunion", "consulta", "dentista", "médico", "médica"]:
        if word in words:
            return word
    return text.split()[-1] if text.split() else ""

def _extract_name_type(text: str) -> tuple[str, str]:
    words = text.lower().split()
    name = ""
    apt_type = "otra"
    for word in words:
        if word in ["médica", "medica", "médico", "medico"]:
            apt_type = "médica"
        elif word in ["personal"]:
            apt_type = "personal"
        elif word in ["trabajo", "reunión", "reunion"]:
            apt_type = "trabajo"
        elif word not in ["nueva", "cita", "a", "las", "la", "el", "de", "en", "para"]:
            name = word.title()
    return name if name else "Cita", apt_type

def _extract_habit_value(text: str) -> tuple[str, str]:
    text_lower = text.lower()
    for habit in ["dorm", "dormí", "dormi", "sueño"]:
        if habit in text_lower:
            value = _extract_value(text_lower, ["horas", "h", "minutos", "min"])
            return "sueño", value
    for habit in ["agua", "vasos", "litros"]:
        if habit in text_lower:
            value = _extract_value(text_lower, ["vasos", "litros", "l", "ml"])
            return "agua", value
    for habit in ["comida", "comí", "comi"]:
        if habit in text_lower:
            return "comida", text
    return "", ""

def _extract_value(text: str, units: List[str]) -> str:
    for unit in units:
        if unit in text:
            parts = text.split()
            for part in parts:
                if part == unit or (unit in part and part.replace(unit, "").isdigit()):
                    return part
    numbers = [w for w in text.split() if w.replace(".", "").isdigit()]
    return numbers[0] if numbers else ""
