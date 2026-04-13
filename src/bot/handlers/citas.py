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

Scheduler (F12):
    Al crear una cita → schedule_apt_reminders()
    Al borrar una cita → cancel_apt_reminders()
    Al editar la hora de una cita → cancel + re-schedule
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

logger = logging.getLogger(__name__)
api    = ThdoraApiClient()

_RE_TIME = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")

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
EDIT_APT_TIME, EDIT_APT_NOMBRE, EDIT_APT_TYPE, EDIT_APT_NOTES = range(20, 24)


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
    parts    = query.data.split("_", 3)
    date_str = parts[2]
    idx      = int(parts[3])
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
    query = update.callback_query
    await query.answer()
    _, date_str, idx_str = query.data.split("_", 2)
    await query.edit_message_reply_markup(reply_markup=_kb_apt_confirm(date_str, int(idx_str)))


async def cb_apt_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _, date_str, idx_str = query.data.split("_", 2)
    user_id = str(query.from_user.id)
    apt_id  = int(idx_str)
    try:
        ok  = await api.delete_appointment(date_str, apt_id)
        if ok:
            # Cancelar jobs pendientes de esta cita
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
    context.user_data["nueva_time"] = time_str
    date_str = context.user_data.get("nueva_date", str(date.today()))
    try:
        conflict = await api.check_appointment_conflict(date_str, time_str)
        if conflict:
            nc  = conflict.get("name") or conflict.get("type", "cita")
            txt = (
                f"⚠️ *Ya tienes una cita a las {time_str}:* _{nc}_\n\n"
                f"¿Crear de todas formas o cambiar hora?"
            )
            if is_message:
                await obj.message.reply_text(txt, parse_mode="Markdown", reply_markup=_kb_conflict_apt())
            else:
                await obj.edit_message_text(txt, parse_mode="Markdown", reply_markup=_kb_conflict_apt())
            return NUEVA_CONFLICT
    except Exception:
        pass
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
        # Programar avisos de esta cita según config del usuario
        try:
            cfg = await api.get_user_config(user_id)
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

async def cb_apt_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, date_str, idx_str = query.data.split("_", 2)
    context.user_data["edit_apt_date"]  = date_str
    context.user_data["edit_apt_index"] = int(idx_str)
    await query.edit_message_text(
        f"✏️ *Editar cita {idx_str} del {date_str}*\n\nNueva hora \\(HH:MM\\) o /skip:",
        parse_mode="Markdown",
    )
    return EDIT_APT_TIME


async def cb_apt_edit_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() != "/skip":
        if not _RE_TIME.match(text):
            await update.message.reply_text(
                "❌ Formato incorrecto\\. Usa `HH:MM` o /skip\\.", parse_mode="Markdown"
            )
            return EDIT_APT_TIME
        context.user_data["edit_apt_time"] = text
    await update.message.reply_text("Nuevo nombre o /skip:")
    return EDIT_APT_NOMBRE


async def cb_apt_edit_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() != "/skip":
        context.user_data["edit_apt_nombre"] = text
    await update.message.reply_text(
        "Nuevo tipo o /skip:",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(t.capitalize(), callback_data=f"etipo_{t}") for t in TIPOS_CITA]]
            + [[InlineKeyboardButton("⏭️ Skip", callback_data="etipo_skip")]]
        ),
    )
    return EDIT_APT_TYPE


async def cb_apt_edit_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.replace("etipo_", "")
    if value != "skip":
        context.user_data["edit_apt_type"] = value
    await query.edit_message_text("Nuevas notas o /skip:")
    return EDIT_APT_NOTES


async def cb_apt_edit_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text     = update.message.text.strip()
    notes    = text if text.lower() != "/skip" else None
    date_str = context.user_data.get("edit_apt_date", "")
    index    = context.user_data.get("edit_apt_index", 0)
    user_id  = str(update.effective_user.id)
    try:
        result = await api.update_appointment(
            date_str, index,
            time=context.user_data.get("edit_apt_time"),
            name=context.user_data.get("edit_apt_nombre"),
            apt_type=context.user_data.get("edit_apt_type"),
            notes=notes,
        )
        # Reprogramar avisos si la hora cambió
        if context.user_data.get("edit_apt_time") and result:
            try:
                cancel_apt_reminders(user_id, index)
                cfg = await api.get_user_config(user_id)
                schedule_apt_reminders(update.get_bot(), user_id, result, cfg)
            except Exception as sched_err:
                logger.warning("No se pudo reprogramar reminder: %s", sched_err)
        await update.message.reply_text(
            f"✅ *Cita {index} actualizada\\.*",
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


async def _skip_to(update, context, next_state, prompt):
    await update.message.reply_text(prompt)
    return next_state


async def _skip_to_type(update, context):
    await update.message.reply_text(
        "Nuevo tipo o /skip:",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(t.capitalize(), callback_data=f"etipo_{t}") for t in TIPOS_CITA]]
            + [[InlineKeyboardButton("⏭️ Skip", callback_data="etipo_skip")]]
        ),
    )
    return EDIT_APT_TYPE


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
            EDIT_APT_TIME: [
                CommandHandler("skip", lambda u, c: _skip_to(u, c, EDIT_APT_NOMBRE, "Nuevo nombre o /skip:")),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_time),
            ],
            EDIT_APT_NOMBRE: [
                CommandHandler("skip", _skip_to_type),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_nombre),
            ],
            EDIT_APT_TYPE:  [CallbackQueryHandler(cb_apt_edit_type, pattern=r"^etipo_")],
            EDIT_APT_NOTES: [
                CommandHandler("skip", lambda u, c: cb_apt_edit_notes(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_notes),
            ],
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
