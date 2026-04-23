"""
Handlers de citas: /citas, /nueva (con franjas horarias), editar, borrar, detalle.

Flujo /nueva con franjas:
    NUEVA_DATE       → fecha (texto libre)
    NUEVA_FRANJA     → 🌅 Mañana / 🏆 Tarde / 🌙 Noche / ✏️ Exacta
    NUEVA_HORA_PUNTO → hora en punto con botones de la franja
    NUEVA_HORA_CUARTO→ (opcional) :00 :15 :30 :45
    NUEVA_TIME       → hora exacta si el usuario quiere escribirla
    NUEVA_CONFLICT   → aviso de conflicto de hora
    NUEVA_NOMBRE     → nombre libre
    NUEVA_TYPE       → tipo [médica / personal / trabajo / otra]
    NUEVA_NOTES      → notas o /skip

Detalle del estado NUEVA_CONFLICT (v0.15.1):
    Cuando la API detecta solapamiento (check_appointment_conflict devuelve
    la cita existente), el bot muestra:
      1. Nombre y rango completo de la cita que bloquea: Dentista (17:00–18:00)
      2. Horario visual del día mediante _build_day_schedule (importado de nlp.py)
         con el slot solicitado marcado como ⚠️.
    El usuario puede entonces elegir cambiar hora o crear de todas formas.

Flujo editar cita (build_edit_apt_handler):
    Entrada: callback ae_{date_str}_{index}
    EDIT_APT_FIELD   → el usuario elige qué campo editar (botones)
    EDIT_APT_TIME    → nueva hora (HH:MM) — comprueba conflicto igual que /nueva
    EDIT_APT_NOMBRE  → nuevo nombre
    EDIT_APT_TYPE    → nuevo tipo (botones)
    EDIT_APT_NOTES   → nuevas notas
    Guarda y vuelve al día.

Comprobación de solapamiento (v0.15.1):
    Tanto /nueva como editar hora usan la misma función _check_and_show_conflict.
    Esta función llama a api.check_appointment_conflict (que a su vez usa
    _find_overlap en appointments.py con duración real de 60 min) y, si hay
    conflicto, monta el mensaje con nombre + rango + horario visual del día.

Scheduler (F12):
    Al crear una cita  → schedule_apt_reminders()
    Al borrar una cita → cancel_apt_reminders()
    Al editar la hora  → cancel + re-schedule

Nota sobre callback_data con fechas:
    Los prefijos ae_, ad_, adc_ usan el patrón {prefix}{date_str}_{index}.
    La fecha contiene guiones (2026-04-13), así que NO usar split('_', 2).
    Se extrae con: data[len(prefix):] y luego rsplit('_', 1).

Cambios v0.16 (2026-04-23):
    - cb_apt_delete: muestra nombre + hora de la cita antes de pedir confirmación
      (UX: el usuario sabe exactamente qué va a borrar — tarea 1.3)
"""

import re
import logging
from datetime import date
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
_DEFAULT_DURATION = 60  # minutos, igual que en appointments.py

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
    """
    Extrae (date_str, index) de un callback_data con formato:
        {prefix}{date_str}_{index}
    Ejemplo: 'ae_2026-04-13_0' con prefix='ae_' → ('2026-04-13', 0)

    NO usar split('_', 2) porque la fecha contiene guiones.
    """
    rest = data[len(prefix):]
    date_str, idx_str = rest.rsplit("_", 1)
    return date_str, int(idx_str)


# ═══════════════════════════════════════════════════════════════════════
# HELPER DE CONFLICTO (v0.15.1)
# ═══════════════════════════════════════════════════════════════════════

async def _check_and_show_conflict(
    obj,
    context: ContextTypes.DEFAULT_TYPE,
    date_str: str,
    time_str: str,
    is_message: bool = False,
) -> Optional[int]:
    """
    Comprueba solapamiento llamando a la API y, si lo hay, muestra:
      - Nombre y rango de la cita existente (ej: Dentista 17:00–18:00)
      - Horario visual del día con el slot solicitado marcado como ⚠️

    Devuelve NUEVA_CONFLICT si hay conflicto, None si no.
    Usado tanto en /nueva como en editar hora para mantener consistencia.

    Diseño de degradación elegante:
      Si la API falla, devuelve None y el flujo continúa sin bloquear al usuario.
    """
    try:
        conflict = await api.check_appointment_conflict(date_str, time_str)
    except Exception:
        return None

    if not conflict:
        return None

    # Nombre de la cita que bloquea el slot
    nc       = conflict.get("name") or conflict.get("type", "cita")
    ct       = conflict.get("time", "?")
    ct_end   = _end_time(ct, _DEFAULT_DURATION)

    # Horario visual del día con el slot solicitado marcado como ⚠️
    try:
        apts  = await api.get_appointments(date_str)
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
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    await _show_citas(update.message, date_str)


async def _show_citas(msg, date_str: str) -> None:
    try:
        apts = await api.get_appointments(date_str)
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
    query = update.callback_query
    await query.answer()
    date_str = query.data.replace("citas_nav_", "")
    await _show_citas(query.message, date_str)


async def cb_cita_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str, idx = _parse_apt_callback("cita_detail_", query.data)
    try:
        apts = await api.get_appointments(date_str)
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
    """
    Primer paso del borrado: muestra nombre + hora de la cita y pide confirmación.

    v0.16: antes sólo editaba el reply_markup (botones) sin mostrar qué cita
    se iba a borrar. Ahora hace GET de la cita y muestra:
        🗑️ ¿Borrar esta cita?
          ⏰ HH:MM — Nombre [tipo]
        ⚠️ Esta acción no se puede deshacer.
    """
    query = update.callback_query
    await query.answer()
    date_str, idx = _parse_apt_callback("ad_", query.data)

    # Obtener datos de la cita para mostrárselos al usuario
    nombre = "cita"
    hora   = "?"
    tipo   = ""
    try:
        apts = await api.get_appointments(date_str)
        apt  = next((a for a in apts if a.get("index") == idx), None)
        if apt:
            nombre = apt.get("name", "") or apt.get("type", "cita")
            hora   = apt.get("time", "?")
            tipo   = f" \\[{apt['type']}\\]" if apt.get("type") else ""
    except Exception:
        pass  # degradación elegante: si falla la API mostramos igual la confirmación

    await query.edit_message_text(
        f"🗑️ *¿Borrar esta cita?*\n\n"
        f"  ⏰ *{hora}* — {nombre}{tipo}\n\n"
        f"⚠️ _Esta acción no se puede deshacer\\._",
        parse_mode="Markdown",
        reply_markup=_kb_apt_confirm(date_str, idx),
    )


async def cb_apt_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str, apt_id = _parse_apt_callback("adc_", query.data)
    user_id = str(query.from_user.id)
    try:
        ok  = await api.delete_appointment(date_str, apt_id)
        if ok:
            cancel_apt_reminders(user_id, apt_id)
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
    if data.startswith("quick_nueva_"):
        fecha = data.replace("quick_nueva_", "")
    else:
        fecha = str(date.today())
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
    franja_labels = {"manana": "🌅 Mañana", "tarde": "🏆 Tarde", "noche": "🌙 Noche"}
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
        hora_inicio = {"manana": 6, "tarde": 14, "noche": 22}[franja]
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
    """
    Punto de entrada común tras elegir hora (botón o texto libre).

    1. Guarda la hora en user_data.
    2. Llama a _check_and_show_conflict.
       - Si hay conflicto → muestra nombre + rango + horario visual → NUEVA_CONFLICT.
       - Si no hay conflicto → pide nombre → NUEVA_NOMBRE.
    """
    context.user_data["nueva_time"] = time_str
    date_str = context.user_data.get("nueva_date", str(date.today()))

    result = await _check_and_show_conflict(obj, context, date_str, time_str, is_message=is_message)
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
    d  = context.user_data.get("nueva_date", str(date.today()))
    t  = context.user_data.get("nueva_time", "")
    nm = context.user_data.get("nueva_nombre", "")
    tp = context.user_data.get("nueva_type", "otra")
    try:
        result  = await api.create_appointment(d, t, nm, tp, notes)
        user_id = str(update.effective_user.id)
        try:
            cfg = await api.get_user_config(user_id)
            if "date" not in result:
                result["date"] = result.get("date_str", d)
            schedule_apt_reminders(update.get_bot(), user_id, result, cfg)
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
    """Teclado para elegir qué campo de la cita editar."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏰ Hora",    callback_data=f"aedit_time_{date_str}_{idx}")],
        [InlineKeyboardButton("📝 Nombre",  callback_data=f"aedit_name_{date_str}_{idx}")],
        [InlineKeyboardButton("🏷 Tipo",    callback_data=f"aedit_type_{date_str}_{idx}")],
        [InlineKeyboardButton("💬 Notas",   callback_data=f"aedit_notes_{date_str}_{idx}")],
        [InlineKeyboardButton("← Cancelar", callback_data=f"citas_nav_{date_str}")],
    ])


async def cb_apt_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    date_str, idx = _parse_apt_callback("ae_", query.data)
    context.user_data["edit_apt_date"]  = date_str
    context.user_data["edit_apt_index"] = idx
    try:
        apts = await api.get_appointments(date_str)
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
    """El usuario eligió qué campo editar."""
    query = update.callback_query
    await query.answer()
    data  = query.data  # aedit_{field}_{date_str}_{idx}
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
    context.user_data["edit_apt_time"] = text

    result = await _check_and_show_conflict(
        update, context, date_str, text, is_message=True
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
    """Guarda el campo editado y vuelve al día."""
    date_str = context.user_data.get("edit_apt_date", "")
    index    = context.user_data.get("edit_apt_index", 0)
    user_id  = str(update.effective_user.id)
    try:
        result = await api.update_appointment(
            date_str, index,
            time=context.user_data.get("edit_apt_time"),
            name=context.user_data.get("edit_apt_nombre"),
            apt_type=context.user_data.get("edit_apt_type"),
            notes=context.user_data.get("edit_apt_notes"),
        )
        if context.user_data.get("edit_apt_time") and result:
            try:
                cancel_apt_reminders(user_id, index)
                cfg = await api.get_user_config(user_id)
                if "date" not in result:
                    result["date"] = result.get("date_str", date_str)
                schedule_apt_reminders(update.get_bot(), user_id, result, cfg)
            except Exception as sched_err:
                logger.warning("No se pudo reprogramar reminder: %s", sched_err)
        await update.message.reply_text(
            f"✅ *Cita actualizada\\.*",
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
    """Versión de _do_update_apt para cuando la respuesta viene de un CallbackQuery."""
    date_str = context.user_data.get("edit_apt_date", "")
    index    = context.user_data.get("edit_apt_index", 0)
    user_id  = str(query.from_user.id)
    try:
        await api.update_appointment(
            date_str, index,
            time=context.user_data.get("edit_apt_time"),
            name=context.user_data.get("edit_apt_nombre"),
            apt_type=context.user_data.get("edit_apt_type"),
            notes=context.user_data.get("edit_apt_notes"),
        )
        await query.edit_message_text(
            f"✅ *Cita actualizada\\.*",
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
    from telegram.ext import ConversationHandler
    await update.message.reply_text(
        "❌ Operación cancelada\\.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Menú", callback_data="menu_home")
        ]]),
    )
    return ConversationHandler.END
