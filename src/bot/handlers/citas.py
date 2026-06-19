"""
Handlers de citas: /citas, /nueva (con franjas horarias), editar, borrar, detalle.

Flujo /nueva con franjas:
    NUEVA_DATE       → fecha (texto libre)
    NUEVA_FRANJA     → 🌅 Mañana / 🌆 Tarde / 🌙 Noche / ✏️ Exacta
    NUEVA_HORA_PUNTO → hora en punto con botones de la franja
    NUEVA_HORA_CUARTO→ (opcional) :00 :15 :30 :45
    NUEVA_TIME       → hora exacta si el usuario quiere escribirla
    NUEVA_CONFLICT   → aviso de conflicto de hora
    NUEVA_NOMBRE     → nombre libre
    NUEVA_TYPE       → tipo [médica / personal / trabajo / otra]
    NUEVA_NOTES      → notas o /skip

Fixes v0.17 (2026-06-20):
    - B12-B16: todas las llamadas a api.* corregidas con user_id obligatorio
               y firmas correctas según ThdoraApiClient v5
    - B16: check_appointment_conflict no existe en api_client → detección
           de solapamiento implementada localmente con get_appointments
"""

import re
import logging
from datetime import date, datetime
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.api_client import ApiError, ThdoraApiClient
from src.bot.keyboards import (
    _kb_back, _kb_tipos, _kb_franjas, _kb_horas_franja, _kb_cuartos,
    _kb_apt_confirm, _kb_cita_detail, _kb_conflict_apt, _nav_keyboard,
    TIPOS_CITA,
)
from src.bot.utils.dates import _parse_date_flex, _parse_date_arg, _date_label, _date_short
from src.bot.scheduler import schedule_apt_reminders, cancel_apt_reminders
from src.bot.handlers.nlp import _build_day_schedule, _end_time

logger = logging.getLogger(__name__)
api    = ThdoraApiClient()

_RE_TIME = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
_DEFAULT_DURATION = 60  # minutos

# ── Estados ConversationHandler /nueva ───────────────────────────────
(
    NUEVA_DATE,
    NUEVA_FRANJA,
    NUEVA_HORA_PUNTO,
    NUEVA_HORA_CUARTO,
    NUEVA_TIME,
    NUEVA_CONFLICT,
    NUEVA_NOMBRE,
    NUEVA_TYPE,
    NUEVA_NOTES,
) = range(9)

# ── Estados editar cita ───────────────────────────────────────────
EDIT_APT_FIELD, EDIT_APT_TIME, EDIT_APT_NOMBRE, EDIT_APT_TYPE, EDIT_APT_NOTES = range(20, 25)


def _parse_apt_callback(prefix: str, data: str):
    rest = data[len(prefix):]
    date_str, idx_str = rest.rsplit("_", 1)
    return date_str, int(idx_str)


def _find_overlap(apts: list, time_str: str, duration: int = 60) -> Optional[dict]:
    """Detecta solapamiento local: devuelve la cita que solapa con time_str o None."""
    try:
        h, m = map(int, time_str.split(":"))
        new_start = h * 60 + m
        new_end   = new_start + duration
    except Exception:
        return None
    for apt in apts:
        t = apt.get("time", "")
        try:
            ah, am = map(int, t.split(":"))
            apt_start = ah * 60 + am
            apt_end   = apt_start + duration
            if new_start < apt_end and new_end > apt_start:
                return apt
        except Exception:
            continue
    return None


# ═══════════════════════════════════════════════════════════════════════
# HELPER DE CONFLICTO (v0.17 — detección local, sin endpoint externo)
# ═══════════════════════════════════════════════════════════════════════

async def _check_and_show_conflict(
    obj,
    context: ContextTypes.DEFAULT_TYPE,
    date_str: str,
    time_str: str,
    user_id: int,
    is_message: bool = False,
) -> Optional[int]:
    try:
        apts = await api.get_appointments(date_str, user_id)
    except Exception:
        return None

    conflict = _find_overlap(apts, time_str, _DEFAULT_DURATION)
    if not conflict:
        return None

    nc     = conflict.get("name") or conflict.get("type", "cita")
    ct     = conflict.get("time", "?")
    ct_end = _end_time(ct, _DEFAULT_DURATION)

    try:
        sched = _build_day_schedule(apts, date_str, highlight_time=time_str, duration=_DEFAULT_DURATION)
        sched_block = f"\n\n{sched}"
    except Exception:
        sched_block = ""

    txt = (
        f"⚠️ *Las {time_str} solapan con _{nc}_ ({ct}–{ct_end})*\n"
        f"Esa franja ya está ocupada.{sched_block}\n\n"
        f"¿Crear de todas formas o cambiar hora?"
    )
    if is_message:
        await obj.message.reply_text(txt, parse_mode="Markdown", reply_markup=_kb_conflict_apt())
    else:
        await obj.edit_message_text(txt, parse_mode="Markdown", reply_markup=_kb_conflict_apt())
    return NUEVA_CONFLICT


# ═══════════════════════════════════════════════════════════════════════
# VISTAS
# ═══════════════════════════════════════════════════════════════════════

async def cmd_citas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from src.bot.utils.accum import _clean_acum_context
    _clean_acum_context(context)
    user_id  = update.effective_user.id
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    await _show_citas(update.message, date_str, user_id)


async def _show_citas(msg, date_str: str, user_id: int) -> None:
    try:
        apts = await api.get_appointments(date_str, user_id)
    except ApiError:
        await msg.reply_text("⚠️ Error al conectar con la API.")
        return

    label = _date_label(date_str)
    nav   = _nav_keyboard(date_str, "citas")

    if not apts:
        await msg.reply_text(
            f"📅 No hay citas el *{label}*\\.",
            parse_mode="Markdown",
            reply_markup=nav,
        )
        return

    await msg.reply_text(
        f"📅 *Citas del {label}:*",
        parse_mode="Markdown",
        reply_markup=nav,
    )
    for apt in apts:
        idx    = apt.get("index", 0)
        nombre = apt.get("name", "") or apt.get("type", "")
        notas  = f"\n📝 _{apt['notes']}_" if apt.get("notes") else ""
        await msg.reply_text(
            f"⏰ *{apt['time']}* — {nombre} \\[{apt['type']}\\]{notas}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"⏰ {apt['time']}", callback_data=f"cita_detail_{date_str}_{idx}"),
                InlineKeyboardButton("✏️", callback_data=f"ae_{date_str}_{idx}"),
                InlineKeyboardButton("🗑️", callback_data=f"ad_{date_str}_{idx}"),
            ]]),
        )


async def cb_citas_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = query.from_user.id
    date_str = query.data.replace("citas_nav_", "")
    await _show_citas(query.message, date_str, user_id)


async def cb_cita_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = query.from_user.id
    date_str, idx = _parse_apt_callback("cita_detail_", query.data)
    try:
        apts = await api.get_appointments(date_str, user_id)
    except ApiError:
        await query.message.reply_text("⚠️ Error al obtener la cita.")
        return
    apt = next((a for a in apts if a.get("index") == idx), None)
    if not apt:
        await query.message.reply_text(
            "⚠️ Cita no encontrada\\.",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "citas"),
        )
        return
    nombre = apt.get("name", "") or apt.get("type", "—")
    notas  = apt.get("notes") or "—"
    label  = _date_label(date_str)
    await query.message.reply_text(
        f"📅 *Detalle de cita*\n\n"
        f"  🗓 *Fecha:* {label}\n"
        f"  ⏰ *Hora:* {apt['time']}\n"
        f"  📝 *Nombre:* {nombre}\n"
        f"  🏷 *Tipo:* {apt['type']}\n"
        f"  💬 *Notas:* {notas}",
        parse_mode="Markdown",
        reply_markup=_kb_cita_detail(date_str, idx),
    )


# ═══════════════════════════════════════════════════════════════════════
# BORRAR CITA
# ═══════════════════════════════════════════════════════════════════════

async def cb_apt_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = query.from_user.id
    date_str, idx = _parse_apt_callback("ad_", query.data)

    nombre = "cita"
    hora   = "?"
    tipo   = ""
    try:
        apts = await api.get_appointments(date_str, user_id)
        apt  = next((a for a in apts if a.get("index") == idx), None)
        if apt:
            nombre = apt.get("name", "") or apt.get("type", "cita")
            hora   = apt.get("time", "?")
            tipo   = f" \\[{apt['type']}\\]" if apt.get("type") else ""
    except Exception:
        pass

    await query.edit_message_text(
        f"🗑️ *¿Borrar esta cita?*\n\n"
        f"  ⏰ *{hora}* — {nombre}{tipo}\n\n"
        f"⚠️ _Esta acción no se puede deshacer\\._",
        parse_mode="Markdown",
        reply_markup=_kb_apt_confirm(date_str, idx),
    )


async def cb_apt_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = query.from_user.id
    date_str, apt_id = _parse_apt_callback("adc_", query.data)
    try:
        ok = await api.delete_appointment(date_str, apt_id, user_id)
        if ok:
            cancel_apt_reminders(str(user_id), apt_id)
        txt = "🗑️ Cita eliminada\\." if ok else "⚠️ Cita no encontrada \\(ya borrada\\)\\."
        await query.edit_message_text(
            txt, parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "citas"),
        )
    except ApiError:
        await query.edit_message_text("⚠️ Error al borrar la cita\\.", parse_mode="Markdown")


# ═══════════════════════════════════════════════════════════════════════
# /nueva — ConversationHandler con FRANJAS HORARIAS
# ═══════════════════════════════════════════════════════════════════════

async def nueva_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "📅 *Nueva cita — paso 1/6*\n\n¿Para qué fecha?\n`hoy`, `mañana`, `27/03`…",
        parse_mode="Markdown",
    )
    return NUEVA_DATE


async def nueva_start_desde_boton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    data = query.data
    fecha = data.replace("quick_nueva_", "") if data.startswith("quick_nueva_") else str(date.today())
    context.user_data["nueva_date"] = fecha
    await query.message.reply_text(
        f"📅 *Nueva cita para {_date_short(fecha)}*\n\n"
        f"🕐 *Paso 1/5* — ¿En qué franja del día?",
        parse_mode="Markdown",
        reply_markup=_kb_franjas(),
    )
    return NUEVA_FRANJA


async def nueva_recv_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date_str = _parse_date_flex(update.message.text.strip())
    if not date_str:
        await update.message.reply_text(
            "❌ No entendí la fecha\\. Prueba `hoy`, `mañana` o `2026-03-27`\\.",
            parse_mode="Markdown",
        )
        return NUEVA_DATE
    context.user_data["nueva_date"] = date_str
    await update.message.reply_text(
        f"✅ Fecha: *{_date_short(date_str)}*\n\n"
        f"🕐 *Paso 2/6* — ¿En qué franja del día?",
        parse_mode="Markdown",
        reply_markup=_kb_franjas(),
    )
    return NUEVA_FRANJA


async def nueva_recv_franja(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "franja_exacta":
        await query.edit_message_text(
            "✏️ *Escribe la hora exacta* \\(HH:MM, 24h\\):",
            parse_mode="Markdown",
        )
        return NUEVA_TIME
    franja_key = data.replace("franja_", "")
    context.user_data["nueva_franja"] = franja_key
    franja_labels = {"manana": "🌅 Mañana", "tarde": "🌆 Tarde", "noche": "🌙 Noche"}
    label = franja_labels.get(franja_key, "")
    await query.edit_message_text(
        f"✅ Franja: *{label}*\n\n"
        f"⏰ *Paso 2/5* — ¿A qué hora?",
        parse_mode="Markdown",
        reply_markup=_kb_horas_franja(franja_key),
    )
    return NUEVA_HORA_PUNTO


async def nueva_recv_hora_punto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "hora_exacta":
        await query.edit_message_text(
            "✏️ *Escribe la hora exacta* \\(HH:MM, 24h\\):", parse_mode="Markdown"
        )
        return NUEVA_TIME
    if data == "hora_ver_cuartos":
        franja = context.user_data.get("nueva_franja", "manana")
        _franja_inicio = {"manana": 6, "tarde": 14, "noche": 22}
        hora_inicio = context.user_data.get("nueva_hora_temp") or _franja_inicio.get(franja, 6)
        context.user_data["nueva_hora_temp"] = hora_inicio
        await query.edit_message_text(
            f"🕐 *Elige los cuartos para {hora_inicio:02d}:xx:*",
            parse_mode="Markdown",
            reply_markup=_kb_cuartos(hora_inicio),
        )
        return NUEVA_HORA_CUARTO
    hora = int(data.replace("hora_punto_", ""))
    context.user_data["nueva_hora_temp"] = hora
    await query.edit_message_text(
        f"⏰ Hora: *{hora:02d}:00* seleccionada\n\n¿Quieres afinar los cuartos o confirmar?",
        parse_mode="Markdown",
        reply_markup=_kb_cuartos(hora),
    )
    return NUEVA_HORA_CUARTO


async def nueva_recv_hora_cuarto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "hora_exacta":
        await query.edit_message_text(
            "✏️ *Escribe la hora exacta* \\(HH:MM, 24h\\):", parse_mode="Markdown"
        )
        return NUEVA_TIME
    time_str = data.replace("hora_cuarto_", "")
    return await _after_time_selected(query, context, time_str)


async def nueva_recv_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not _RE_TIME.match(text):
        await update.message.reply_text(
            "❌ Formato incorrecto\\. Usa `HH:MM` \\(ej: `10:30`\\)\\.",
            parse_mode="Markdown",
        )
        return NUEVA_TIME
    return await _after_time_selected(update, context, text, is_message=True)


async def _after_time_selected(obj, context, time_str: str, is_message: bool = False) -> int:
    context.user_data["nueva_time"] = time_str
    date_str = context.user_data.get("nueva_date", str(date.today()))
    user_id  = context.user_data.get("nueva_user_id", 0)

    result = await _check_and_show_conflict(
        obj, context, date_str, time_str, user_id, is_message=is_message
    )
    if result is not None:
        return result

    txt = f"✅ Hora: *{time_str}*\n\n📝 *Paso 3/5* — ¿Cómo se llama la cita?"
    if is_message:
        await obj.message.reply_text(txt, parse_mode="Markdown")
    else:
        await obj.edit_message_text(txt, parse_mode="Markdown")
    return NUEVA_NOMBRE


async def nueva_conflict_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "aptconf_ok":
        t = context.user_data.get("nueva_time", "")
        await query.edit_message_text(
            f"✅ Hora: *{t}*\n\n📝 *Paso 3/5* — ¿Cómo se llama la cita?",
            parse_mode="Markdown",
        )
        return NUEVA_NOMBRE
    await query.edit_message_text(
        "🕐 *Elige de nuevo la franja:*", parse_mode="Markdown", reply_markup=_kb_franjas()
    )
    return NUEVA_FRANJA


async def nueva_recv_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("❌ El nombre no puede estar vacío\\.", parse_mode="Markdown")
        return NUEVA_NOMBRE
    context.user_data["nueva_nombre"] = nombre
    await update.message.reply_text(
        f"✅ Nombre: *{nombre}*\n\n📋 *Paso 4/5* — ¿Tipo de cita?",
        parse_mode="Markdown",
        reply_markup=_kb_tipos(),
    )
    return NUEVA_TYPE


async def nueva_recv_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    apt_type = query.data.replace("tipo_", "")
    context.user_data["nueva_type"] = apt_type
    await query.edit_message_text(
        f"✅ Tipo: *{apt_type}*\n\n📝 *Paso 5/5* — ¿Alguna nota? \\(/skip para omitir\\)",
        parse_mode="Markdown",
    )
    return NUEVA_NOTES


async def nueva_recv_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _save_appointment(update, context, update.message.text.strip())


async def nueva_skip_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _save_appointment(update, context, "")


async def _save_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE, notes: str) -> int:
    user_id = update.effective_user.id
    d  = context.user_data.get("nueva_date", str(date.today()))
    t  = context.user_data.get("nueva_time", "")
    nm = context.user_data.get("nueva_nombre", "")
    tp = context.user_data.get("nueva_type", "otra")
    try:
        data   = {"time": t, "name": nm, "type": tp, "notes": notes}
        result = await api.create_appointment(d, data, user_id)
        try:
            cfg = await api.get_user_config(user_id)
            if "date" not in result:
                result["date"] = result.get("date_str", d)
            schedule_apt_reminders(context.bot, str(user_id), result, cfg)
        except Exception as sched_err:
            logger.warning("No se pudo programar reminder: %s", sched_err)
        await update.message.reply_text(
            f"✅ *Cita creada*\n\n"
            f"  📅 {d}  🕰 {t}\n"
            f"  📝 {nm} \\[{tp}\\]\n"
            f"  💬 {notes or '—'}",
            parse_mode="Markdown",
            reply_markup=_kb_back(d, "citas"),
        )
    except ApiError:
        await update.message.reply_text(
            "⚠️ No pude conectar con la API\\. Asegúrate: `make run-api`",
            parse_mode="Markdown",
        )
    context.user_data.clear()
    return ConversationHandler.END


# ═══════════════════════════════════════════════════════════════════════
# EDITAR CITA
# ═══════════════════════════════════════════════════════════════════════

def _kb_edit_apt_fields(date_str: str, idx: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏰ Hora",    callback_data=f"aedit_time_{date_str}_{idx}")],
        [InlineKeyboardButton("📝 Nombre",  callback_data=f"aedit_name_{date_str}_{idx}")],
        [InlineKeyboardButton("🏷 Tipo",    callback_data=f"aedit_type_{date_str}_{idx}")],
        [InlineKeyboardButton("💬 Notas",   callback_data=f"aedit_notes_{date_str}_{idx}")],
        [InlineKeyboardButton("← Cancelar", callback_data=f"citas_nav_{date_str}")],
    ])


async def cb_apt_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query    = update.callback_query
    await query.answer()
    user_id  = query.from_user.id
    date_str, idx = _parse_apt_callback("ae_", query.data)
    context.user_data["edit_apt_date"]    = date_str
    context.user_data["edit_apt_index"]   = idx
    context.user_data["edit_apt_user_id"] = user_id
    try:
        apts = await api.get_appointments(date_str, user_id)
        apt  = next((a for a in apts if a.get("index") == idx), None)
    except ApiError:
        apt = None
    if apt:
        nombre = apt.get("name", "") or apt.get("type", "—")
        context.user_data["edit_apt_current"] = apt
        info = (
            f"✏️ *Editar cita*\n\n"
            f"  ⏰ {apt['time']}  📝 {nombre}\n"
            f"  🏷 {apt['type']}  💬 {apt.get('notes') or '—'}\n\n"
            f"¿Qué quieres cambiar?"
        )
    else:
        info = "✏️ *Editar cita* — ¿Qué quieres cambiar?"
    await query.edit_message_text(
        info, parse_mode="Markdown",
        reply_markup=_kb_edit_apt_fields(date_str, idx),
    )
    return EDIT_APT_FIELD


async def cb_apt_edit_field_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data  = query.data
    rest  = data[len("aedit_"):]
    field, rest2 = rest.split("_", 1)
    date_str, idx = rest2.rsplit("_", 1)
    idx = int(idx)
    context.user_data["edit_apt_field"]  = field
    context.user_data["edit_apt_date"]   = date_str
    context.user_data["edit_apt_index"]  = idx

    if field == "time":
        await query.edit_message_text(
            "⏰ *Nueva hora* \\(HH:MM, 24h\\):", parse_mode="Markdown"
        )
        return EDIT_APT_TIME
    elif field == "name":
        await query.edit_message_text("📝 *Nuevo nombre:*", parse_mode="Markdown")
        return EDIT_APT_NOMBRE
    elif field == "type":
        await query.edit_message_text(
            "🏷 *Nuevo tipo:*", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(t.capitalize(), callback_data=f"etipo_{t}")] for t in TIPOS_CITA]
            ),
        )
        return EDIT_APT_TYPE
    elif field == "notes":
        await query.edit_message_text("💬 *Nuevas notas:*", parse_mode="Markdown")
        return EDIT_APT_NOTES
    return ConversationHandler.END


async def cb_apt_edit_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not _RE_TIME.match(text):
        await update.message.reply_text(
            "❌ Formato incorrecto\\. Usa `HH:MM` \\(ej: `10:30`\\)\\.",
            parse_mode="Markdown",
        )
        return EDIT_APT_TIME

    date_str = context.user_data.get("edit_apt_date", "")
    user_id  = context.user_data.get("edit_apt_user_id", update.effective_user.id)
    context.user_data["edit_apt_time"] = text

    result = await _check_and_show_conflict(
        update, context, date_str, text, user_id, is_message=True
    )
    if result is not None:
        context.user_data["edit_conflict_pending"] = True
        return NUEVA_CONFLICT

    return await _do_update_apt(update, context)


async def cb_apt_edit_conflict_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.pop("edit_conflict_pending", None)
    if query.data == "aptconf_ok":
        return await _do_update_apt_from_query(query, context)
    await query.edit_message_text(
        "⏰ *Nueva hora* \\(HH:MM, 24h\\):", parse_mode="Markdown"
    )
    return EDIT_APT_TIME


async def cb_apt_edit_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["edit_apt_nombre"] = update.message.text.strip()
    return await _do_update_apt(update, context)


async def cb_apt_edit_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["edit_apt_type"] = query.data.replace("etipo_", "")
    return await _do_update_apt_from_query(query, context)


async def cb_apt_edit_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["edit_apt_notes"] = update.message.text.strip()
    return await _do_update_apt(update, context)


async def _do_update_apt(update: Update, context) -> int:
    date_str = context.user_data.get("edit_apt_date", "")
    index    = context.user_data.get("edit_apt_index", 0)
    user_id  = context.user_data.get("edit_apt_user_id", update.effective_user.id)
    data = {
        k: v for k, v in {
            "time":  context.user_data.get("edit_apt_time"),
            "name":  context.user_data.get("edit_apt_nombre"),
            "type":  context.user_data.get("edit_apt_type"),
            "notes": context.user_data.get("edit_apt_notes"),
        }.items() if v is not None
    }
    try:
        result = await api.update_appointment(date_str, index, data, user_id)
        if context.user_data.get("edit_apt_time") and result:
            try:
                cancel_apt_reminders(str(user_id), index)
                cfg = await api.get_user_config(user_id)
                if "date" not in result:
                    result["date"] = result.get("date_str", date_str)
                schedule_apt_reminders(context.bot, str(user_id), result, cfg)
            except Exception as sched_err:
                logger.warning("No se pudo reprogramar reminder: %s", sched_err)
        await update.message.reply_text(
            "✅ *Cita actualizada\\.*",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "citas"),
        )
    except ApiError:
        await update.message.reply_text(
            "⚠️ No pude conectar con la API\\. Asegúrate: `make run-api`",
            parse_mode="Markdown",
        )
    context.user_data.clear()
    return ConversationHandler.END


async def _do_update_apt_from_query(query, context) -> int:
    date_str = context.user_data.get("edit_apt_date", "")
    index    = context.user_data.get("edit_apt_index", 0)
    user_id  = context.user_data.get("edit_apt_user_id", query.from_user.id)
    data = {
        k: v for k, v in {
            "time":  context.user_data.get("edit_apt_time"),
            "name":  context.user_data.get("edit_apt_nombre"),
            "type":  context.user_data.get("edit_apt_type"),
            "notes": context.user_data.get("edit_apt_notes"),
        }.items() if v is not None
    }
    try:
        await api.update_appointment(date_str, index, data, user_id)
        await query.edit_message_text(
            "✅ *Cita actualizada\\.*",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "citas"),
        )
    except ApiError:
        await query.edit_message_text(
            "⚠️ No pude conectar con la API\\.", parse_mode="Markdown"
        )
    context.user_data.clear()
    return ConversationHandler.END


# ═══════════════════════════════════════════════════════════════════════
# FACTORIES
# ═══════════════════════════════════════════════════════════════════════

def build_nueva_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("nueva", nueva_start),
            CallbackQueryHandler(nueva_start_desde_boton, pattern=r"^quick_nueva"),
        ],
        states={
            NUEVA_DATE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_date)],
            NUEVA_FRANJA:      [CallbackQueryHandler(nueva_recv_franja,      pattern=r"^franja_")],
            NUEVA_HORA_PUNTO:  [CallbackQueryHandler(nueva_recv_hora_punto,  pattern=r"^hora_punto_|^hora_ver_cuartos|^hora_exacta")],
            NUEVA_HORA_CUARTO: [CallbackQueryHandler(nueva_recv_hora_cuarto, pattern=r"^hora_cuarto_|^hora_exacta")],
            NUEVA_TIME:        [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_time)],
            NUEVA_CONFLICT:    [CallbackQueryHandler(nueva_conflict_response, pattern=r"^aptconf_")],
            NUEVA_NOMBRE:      [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_nombre)],
            NUEVA_TYPE:        [CallbackQueryHandler(nueva_recv_type,         pattern=r"^tipo_")],
            NUEVA_NOTES: [
                CommandHandler("skip", nueva_skip_notes),
                MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_notes),
            ],
        },
        fallbacks=[CommandHandler("cancelar", _cmd_cancelar_inline)],
        name="nueva_cita", persistent=False, per_message=False,
    )


def build_edit_apt_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_apt_edit_start, pattern=r"^ae_")],
        states={
            EDIT_APT_FIELD: [
                CallbackQueryHandler(cb_apt_edit_field_chosen, pattern=r"^aedit_"),
            ],
            EDIT_APT_TIME:   [MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_time)],
            EDIT_APT_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_nombre)],
            EDIT_APT_TYPE:   [CallbackQueryHandler(cb_apt_edit_type, pattern=r"^etipo_")],
            EDIT_APT_NOTES:  [MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_notes)],
            NUEVA_CONFLICT:  [CallbackQueryHandler(cb_apt_edit_conflict_response, pattern=r"^aptconf_")],
        },
        fallbacks=[CommandHandler("cancelar", _cmd_cancelar_inline)],
        name="editar_cita", persistent=False, per_message=False,
    )


async def _cmd_cancelar_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Operación cancelada\\.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Menú", callback_data="menu_home")
        ]]),
    )
    return ConversationHandler.END
