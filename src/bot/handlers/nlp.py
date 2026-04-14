"""
Handler de texto libre — modo Toki.

Flujo completo:
    1. Envía ⏳ Procesando... (feedback inmediato)
    2. Consulta contexto real de la API en paralelo:
       — citas de hoy y mañana
       — citas de la semana (1 llamada a /appointments/week/{date})
       — hábitos de hoy
    3. Llama a groq_router.route() con texto + contexto + username
    4. Según el intent ejecuta la acción y responde.

Horario visual:
    _build_day_schedule() genera franjas de 30min entre 08:00 y 22:00.
    Cada cita ocupa su slot de inicio + los siguientes hasta completar 60min.
    🔴 ocupado | 🟢 libre | ⚠️ slot del conflicto solicitado
"""

import asyncio
import logging
from datetime import date, timedelta
from typing import Dict, List

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.api_client import ThdoraApiClient
from src.bot.groq_router import route
from src.bot.keyboards import _kb_start

logger = logging.getLogger(__name__)
api    = ThdoraApiClient()

_DEFAULT_DURATION_MIN = 60   # duración predeterminada de cada cita
_SCHEDULE_START_H     = 8    # primera franja del horario visual
_SCHEDULE_END_H       = 22   # última franja (exclusive)
_SLOT_MIN             = 30   # granularidad del horario visual en minutos

_MSG_MENU = (
    "🤔 No he entendido bien lo que quieres hacer.\n"
    "Usa los botones o escíbeme algo como:\n"
    "  • _\"mañana dentista a las 5\"_\n"
    "  • _\"dormí 7 horas\"_\n"
    "  • _\"cancela el gym de hoy\"_\n"
    "  • _\"mueve el dentista a las 18\"_"
)

_MSG_HORA_CONFIRM = (
    "⏰ No he detectado la hora. ¿A qué hora es la cita _{name}_?\n"
    "Escíbeme la hora (ej: _17:00_) o usa /nueva para el flujo guiado."
)


# ── Horario visual del día ─────────────────────────────────────────────────

def _time_to_min(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _build_day_schedule(
    citas: List[Dict],
    date_str: str,
    highlight_time: str = "",
    duration: int = _DEFAULT_DURATION_MIN,
) -> str:
    """
    Genera el horario visual del día con franjas de _SLOT_MIN minutos.
    - 🔴 slot ocupado por alguna cita (dentro de su bloque de duración)
    - 🟢 slot libre
    - ⚠️ slot solicitado que causó el conflicto
    Al inicio del bloque de cada cita se muestra su nombre.
    """
    # Mapa: minuto_inicio_slot -> etiqueta de cita si ocupa ese slot
    bloques: Dict[int, str] = {}
    for c in citas:
        c_start = _time_to_min(c.get("time", "00:00"))
        c_name  = c.get("name", "Cita")
        # Marcar todos los slots de 30min que ocupa esta cita
        slot = c_start
        while slot < c_start + duration:
            bloques[slot] = c_name if slot == c_start else "┃"  # nombre solo en el 1er slot
            slot += _SLOT_MIN

    highlight_min = _time_to_min(highlight_time) if highlight_time else -1

    lines = [f"📅 *Horario del {date_str}*\n"]
    current = _SCHEDULE_START_H * 60
    end     = _SCHEDULE_END_H   * 60

    while current < end:
        hh = current // 60
        mm = current % 60
        slot_label = f"{hh:02d}:{mm:02d}"

        if current == highlight_min:
            # Slot del conflicto solicitado
            name = bloques.get(current, "")
            if name and name != "┃":
                lines.append(f"⚠️ `{slot_label}` — *{name}* ← ocupada")
            else:
                lines.append(f"⚠️ `{slot_label}` ← solicitada")
        elif current in bloques:
            name = bloques[current]
            if name == "┃":
                lines.append(f"🔴 `{slot_label}`")
            else:
                lines.append(f"🔴 `{slot_label}` — {name}")
        else:
            lines.append(f"🟢 `{slot_label}`")

        current += _SLOT_MIN

    return "\n".join(lines)


# ── Helpers ───────────────────────────────────────────────────────────

def _find_index_by_id(citas: list, cita_id: int) -> int:
    for c in citas:
        if c.get("id") == cita_id:
            return c.get("index", -1)
    return -1


async def _get_api_context(today: str, tomorrow: str) -> dict:
    async def _safe(coro):
        try:
            return await coro
        except Exception:
            return None

    citas, citas_man, habitos, semana_raw = await asyncio.gather(
        _safe(api.get_appointments(today)),
        _safe(api.get_appointments(tomorrow)),
        _safe(api.get_habits(today)),
        _safe(api.get_appointments_week(today)),
    )

    citas      = citas      or []
    citas_man  = citas_man  or []
    habitos    = habitos    or {}
    semana_raw = semana_raw or {}

    semana_lines = []
    for day_str in sorted(semana_raw.keys()):
        if day_str == today:
            continue
        day_citas = semana_raw[day_str]
        if day_citas:
            citas_str = ", ".join(
                f"{c.get('time','?')} {c.get('name','?')}" for c in day_citas
            )
            semana_lines.append(f"  {day_str}: {citas_str}")

    citas_semana = "\n".join(semana_lines) if semana_lines else "ninguna esta semana"

    return {
        "citas":        citas,
        "citas_manana": citas_man,
        "habitos":      habitos,
        "citas_semana": citas_semana,
    }


# ── Handler principal ──────────────────────────────────────────────────

async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    if not text:
        return

    today    = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    username = (
        update.effective_user.first_name
        or update.effective_user.username
        or "Álvaro"
    )

    processing_msg = await update.message.reply_text("⏳ Procesando...")
    api_context    = await _get_api_context(today, tomorrow)

    result = await route(
        text=text,
        user_data=context.user_data,
        api_context=api_context,
        username=username,
    )

    try:
        await processing_msg.delete()
    except Exception:
        pass

    intent    = result["intent"]
    data      = result["data"]
    reply     = result["reply"]
    show_menu = result.get("show_menu", False)

    if show_menu:
        await update.message.reply_text(
            _MSG_MENU, parse_mode="Markdown", reply_markup=_kb_start()
        )
        return

    if reply and not data:
        await update.message.reply_text(reply, parse_mode="Markdown")
        return

    # ── nueva_cita ─────────────────────────────────────────────────────
    if intent == "nueva_cita" and data:
        cita_date  = data.get("date", today)
        cita_time  = data.get("time", "09:00")
        cita_name  = data.get("name", "Cita")
        cita_type  = data.get("type", "otra")
        cita_notes = data.get("notes", "")

        if cita_date == today:
            citas_del_dia = api_context.get("citas", [])
        else:
            try:
                citas_del_dia = await api.get_appointments(cita_date)
            except Exception:
                citas_del_dia = []

        # Fix hora 00:00: mostrar horario para elegir
        if cita_time == "00:00":
            schedule = _build_day_schedule(citas_del_dia, cita_date)
            await update.message.reply_text(
                f"⏰ No he detectado la hora para *{cita_name}*.\n"
                f"Elige una hora libre y respóndeme:\n\n{schedule}",
                parse_mode="Markdown",
            )
            return

        # Conflicto con solapamiento real de 1h → mostrar horario visual
        conflict = await api.check_appointment_conflict(cita_date, cita_time)
        if conflict:
            schedule = _build_day_schedule(
                citas_del_dia, cita_date, highlight_time=cita_time
            )
            await update.message.reply_text(
                f"⚠️ Las *{cita_time}* del {cita_date} solapan con "
                f"*{conflict.get('name', 'una cita')}* "
                f"({conflict.get('time','?')}–{_end_time(conflict.get('time','?'))}).\n"
                f"Elige otra hora libre y respóndeme:\n\n{schedule}",
                parse_mode="Markdown",
            )
            return

        try:
            await api.create_appointment(
                date_str=cita_date, time=cita_time,
                name=cita_name, apt_type=cita_type, notes=cita_notes,
            )
            await update.message.reply_text(
                f"✅ *{cita_name}* añadida el {cita_date} a las {cita_time} ⌟",
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

    # ── borrar_cita ─────────────────────────────────────────────────────
    if intent == "borrar_cita" and data:
        borrar_date = data.get("date", today)
        borrar_id   = data.get("id", -1)
        borrar_name = data.get("name", "")

        citas_actuales = api_context.get("citas", [])
        if borrar_date != today:
            try:
                citas_actuales = await api.get_appointments(borrar_date)
            except Exception:
                citas_actuales = []

        borrar_index = _find_index_by_id(citas_actuales, borrar_id)
        if borrar_index == -1:
            await update.message.reply_text(
                f"⚠️ No encontré la cita *{borrar_name}* en {borrar_date}.\n"
                f"Puede que ya haya sido borrada. Usa /citas para verlas.",
                parse_mode="Markdown", reply_markup=_kb_start(),
            )
            return

        try:
            ok = await api.delete_appointment(date_str=borrar_date, index=borrar_index)
            if ok:
                await update.message.reply_text(
                    f"✅ *{borrar_name or 'Cita'}* eliminada del {borrar_date}.",
                    parse_mode="Markdown", reply_markup=_kb_start(),
                )
            else:
                await update.message.reply_text(
                    f"⚠️ No encontré esa cita en {borrar_date}. Usa /citas para verlas.",
                    reply_markup=_kb_start(),
                )
        except Exception as e:
            logger.error("Error borrando cita desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude borrar la cita ({e}).\nUsa /citas para gestionarlas.",
                reply_markup=_kb_start(),
            )
        return

    # ── editar_cita ─────────────────────────────────────────────────────
    if intent == "editar_cita" and data:
        editar_date  = data.get("date", today)
        editar_id    = data.get("id", -1)
        editar_name  = data.get("name", "Cita")
        new_time     = data.get("new_time")  or None
        new_name     = data.get("new_name")  or None
        new_type     = data.get("new_type")  or None
        new_notes    = data.get("new_notes") or None

        citas_actuales = api_context.get("citas", [])
        if editar_date != today:
            try:
                citas_actuales = await api.get_appointments(editar_date)
            except Exception:
                citas_actuales = []

        editar_index = _find_index_by_id(citas_actuales, editar_id)
        if editar_index == -1:
            await update.message.reply_text(
                f"⚠️ No encontré la cita *{editar_name}* en {editar_date}.\n"
                f"Usa /citas para gestionarlas.",
                parse_mode="Markdown", reply_markup=_kb_start(),
            )
            return

        if new_time == "00:00":
            schedule = _build_day_schedule(citas_actuales, editar_date)
            await update.message.reply_text(
                f"⏰ ¿A qué hora quieres mover *{editar_name}*?\n\n{schedule}",
                parse_mode="Markdown",
            )
            return

        try:
            await api.update_appointment(
                date_str=editar_date, index=editar_index,
                time=new_time, name=new_name, apt_type=new_type, notes=new_notes,
            )
            cambios = []
            if new_time:  cambios.append(f"hora → {new_time}")
            if new_name:  cambios.append(f"nombre → {new_name}")
            if new_type:  cambios.append(f"tipo → {new_type}")
            if new_notes: cambios.append("notas actualizadas")
            cambios_str = ", ".join(cambios) or "sin cambios detectados"
            await update.message.reply_text(
                f"✅ *{editar_name}* actualizada: {cambios_str}.",
                parse_mode="Markdown", reply_markup=_kb_start(),
            )
        except Exception as e:
            logger.error("Error editando cita desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude editar la cita ({e}).\nUsa /citas para gestionarlas.",
                reply_markup=_kb_start(),
            )
        return

    # ── log_habito ──────────────────────────────────────────────────────
    if intent == "log_habito" and data:
        hab_date  = data.get("date", today)
        hab_name  = data.get("habit", "hábito")
        hab_value = data.get("value", "")
        try:
            await api.log_habit(date_str=hab_date, habit=hab_name, value=hab_value)
            await update.message.reply_text(
                f"✅ *{hab_name}*: {hab_value} — registrado",
                parse_mode="Markdown", reply_markup=_kb_start(),
            )
        except Exception as e:
            logger.error("Error registrando hábito desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude registrar el hábito ({e}).\nPrueba con /habito.",
                reply_markup=_kb_start(),
            )
        return

    # ── borrar_habito ────────────────────────────────────────────────────
    if intent == "borrar_habito" and data:
        borrar_hab_date = data.get("date", today)
        borrar_hab_name = data.get("habit", "")
        try:
            ok = await api.delete_habit(date_str=borrar_hab_date, habit=borrar_hab_name)
            if ok:
                await update.message.reply_text(
                    f"✅ *{borrar_hab_name}* eliminado del {borrar_hab_date}.",
                    parse_mode="Markdown", reply_markup=_kb_start(),
                )
            else:
                await update.message.reply_text(
                    f"⚠️ No encontré el hábito *{borrar_hab_name}* en {borrar_hab_date}. "
                    f"Usa /habitos para verlos.",
                    parse_mode="Markdown", reply_markup=_kb_start(),
                )
        except Exception as e:
            logger.error("Error borrando hábito desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude borrar el hábito ({e}).\nUsa /habitos para gestionarlos.",
                reply_markup=_kb_start(),
            )
        return


def _end_time(start: str, duration: int = _DEFAULT_DURATION_MIN) -> str:
    """Calcula la hora de fin dado un inicio 'HH:MM' y duración en minutos."""
    total = _time_to_min(start) + duration
    return f"{total // 60:02d}:{total % 60:02d}"


def _time_to_min(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)
