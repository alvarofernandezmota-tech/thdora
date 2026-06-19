"""
Handlers de hábitos: /habitos, /habito, borrar, editar, sumar.

Fixes v0.17 (2026-06-20):
    - B17-B21: todas las llamadas a api.* corregidas con user_id obligatorio
    - cb_hab_edit_field, _do_edit_habit, factories completos
"""

import logging
from datetime import date

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
    _kb_back, _kb_hab_actions, _kb_hab_confirm, _kb_hab_conflict,
    _kb_hab_value, _nav_keyboard,
    HABIT_TYPE_EMOJIS,
)
from src.bot.utils.accum import _accumulate_value, _clean_acum_context
from src.bot.utils.dates import _parse_date_arg, _date_label, _date_short

logger = logging.getLogger(__name__)
api    = ThdoraApiClient()

# ── Estados /habito ───────────────────────────────────────────────────
HABITO_NOMBRE, HABITO_VALUE, HABITO_CONFLICT = range(10, 13)

# ── Estados editar hábito ─────────────────────────────────────────────
EDIT_HAB_FIELD, EDIT_HAB_NOMBRE, EDIT_HAB_VALUE = range(30, 33)


def _parse_hab_callback(prefix: str, data: str):
    rest     = data[len(prefix):]
    date_str = rest[:10]
    habit    = rest[11:]
    return date_str, habit


# ════════════════════════════════════════════════════════════════════════
# VISTAS
# ════════════════════════════════════════════════════════════════════════

async def cmd_habitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clean_acum_context(context)
    user_id  = update.effective_user.id
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    await _show_habitos(update.message, date_str, user_id)


async def _show_habitos(msg, date_str: str, user_id: int) -> None:
    try:
        habits = await api.get_habits(date_str, user_id)
    except ApiError:
        await msg.reply_text("⚠️ Error al conectar con la API.")
        return
    label = _date_label(date_str)
    nav   = _nav_keyboard(date_str, "habitos")
    if not habits:
        await msg.reply_text(
            f"📊 No hay hábitos el *{label}*\\.",
            parse_mode="Markdown",
            reply_markup=nav,
        )
        return
    await msg.reply_text(
        f"📊 *Hábitos del {label}:*",
        parse_mode="Markdown",
        reply_markup=nav,
    )
    items = habits.items() if isinstance(habits, dict) else [
        (h.get("habit", ""), h.get("value", "")) for h in habits
    ]
    for h, v in items:
        await msg.reply_text(
            f"• *{h}*: `{v}`",
            parse_mode="Markdown",
            reply_markup=_kb_hab_actions(date_str, h),
        )


async def cb_habitos_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = query.from_user.id
    date_str = query.data.replace("habitos_nav_", "")
    await _show_habitos(query.message, date_str, user_id)


# ════════════════════════════════════════════════════════════════════════
# BORRAR / SUMAR
# ════════════════════════════════════════════════════════════════════════

async def cb_hab_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str, habit = _parse_hab_callback("hd_", query.data)
    await query.edit_message_reply_markup(reply_markup=_kb_hab_confirm(date_str, habit))


async def cb_hab_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = query.from_user.id
    date_str, habit = _parse_hab_callback("hdc_", query.data)
    try:
        ok  = await api.delete_habit(date_str, habit, user_id)
        txt = "🗑️ Hábito eliminado\\." if ok else "⚠️ Hábito no encontrado \\(ya borrado\\)\\."
        await query.edit_message_text(
            txt, parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await query.edit_message_text("⚠️ Error al borrar el hábito\\.", parse_mode="Markdown")


async def cb_hab_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str, habit = _parse_hab_callback("ha_", query.data)
    context.user_data["acum_hab_date"]    = date_str
    context.user_data["acum_hab_nombre"]  = habit
    context.user_data["acum_hab_user_id"] = query.from_user.id
    await query.edit_message_text(
        f"➕ *Sumar a '{habit}'*\n\n"
        "Incremento \\(ej: `+2`, `+30min`, `+1.5L`\\)\n"
        "O escribe el nuevo valor directo para sobreescribir:",
        parse_mode="Markdown",
    )


async def cb_hab_add_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    new_input = update.message.text.strip()
    date_str  = context.user_data.get("acum_hab_date", "")
    habit     = context.user_data.get("acum_hab_nombre", "")
    user_id   = context.user_data.get("acum_hab_user_id", update.effective_user.id)
    if not date_str or not habit:
        return
    try:
        habits      = await api.get_habits(date_str, user_id)
        existing    = habits.get(habit) if isinstance(habits, dict) else next(
            (h.get("value") for h in habits if h.get("habit") == habit), None
        )
        final_value = _accumulate_value(existing, new_input)
        await api.log_habit(date_str, habit, final_value, user_id)
        op = "acumulado" if new_input.startswith("+") else "actualizado"
        await update.message.reply_text(
            f"✅ *{habit}* {op}: `{existing or '0'}` → `{final_value}`",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await update.message.reply_text(
            "⚠️ No pude conectar con la API\\. Asegúrate: `make run-api`",
            parse_mode="Markdown",
        )
    _clean_acum_context(context)


# ════════════════════════════════════════════════════════════════════════
# /habito — ConversationHandler
# ════════════════════════════════════════════════════════════════════════

async def habito_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data["habito_date"]    = str(date.today())
    context.user_data["habito_user_id"] = update.effective_user.id
    await update.message.reply_text(
        f"📊 *Nuevo hábito para {_date_short(str(date.today()))}*\n\n✏️ *Paso 1/2* — ¿Cómo se llama el hábito?",
        parse_mode="Markdown",
    )
    return HABITO_NOMBRE


async def habito_start_desde_boton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    data  = query.data
    fecha = data.replace("quick_habito_", "") if data.startswith("quick_habito_") else str(date.today())
    context.user_data["habito_date"]    = fecha
    context.user_data["habito_user_id"] = query.from_user.id
    await query.message.reply_text(
        f"📊 *Nuevo hábito para {_date_short(fecha)}*\n\n✏️ *Paso 1/2* — ¿Cómo se llama el hábito?",
        parse_mode="Markdown",
    )
    return HABITO_NOMBRE


async def habito_recv_nombre_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("❌ El nombre no puede estar vacío\\.", parse_mode="Markdown")
        return HABITO_NOMBRE
    context.user_data["habito_nombre"] = nombre
    return await _ask_habito_value(update.message, context, nombre)


async def _ask_habito_value(msg, context, nombre: str) -> int:
    user_id = context.user_data.get("habito_user_id", 0)
    try:
        cfg = await api.get_habit_config(nombre, user_id)
    except Exception:
        cfg = None
    kb   = _kb_hab_value(cfg)
    hint = ""
    if cfg:
        htype = cfg.get("habit_type", "text")
        unit  = cfg.get("unit") or ""
        hint  = f" \\({HABIT_TYPE_EMOJIS.get(htype, '')} {htype}{' · ' + unit if unit else ''}\\)"
    prompt = f"✅ Hábito: *{nombre}*{hint}\n\n📊 *Paso 2/2* — ¿Cuál es el valor?"
    if kb:
        await msg.reply_text(prompt, parse_mode="Markdown", reply_markup=kb)
    else:
        await msg.reply_text(
            prompt + " \\(ej: `8h`, `30min`, `2L`\\)\nUsa `+N` para acumular\\.",
            parse_mode="Markdown",
        )
    return HABITO_VALUE


async def habito_recv_value_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.replace("hval_", "")
    if value == "__otro":
        await query.edit_message_text("✏️ Escribe el valor:")
        return HABITO_VALUE
    return await _save_habito(query.message, context, value)


async def habito_recv_value_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text.strip()
    if not value:
        await update.message.reply_text("❌ El valor no puede estar vacío\\.", parse_mode="Markdown")
        return HABITO_VALUE
    return await _save_habito(update.message, context, value)


async def _save_habito(msg, context, new_input: str) -> int:
    nombre   = context.user_data.get("habito_nombre", "")
    date_str = context.user_data.get("habito_date", str(date.today()))
    user_id  = context.user_data.get("habito_user_id", 0)
    try:
        habits   = await api.get_habits(date_str, user_id)
        existing = habits.get(nombre) if isinstance(habits, dict) else next(
            (h.get("value") for h in habits if h.get("habit") == nombre), None
        )
        if existing and not new_input.startswith("+"):
            context.user_data["habito_new_val"]      = new_input
            context.user_data["habito_existing_val"] = existing
            await msg.reply_text(
                f"⚠️ *{nombre}* ya tiene `{existing}` hoy\\.\n¿Qué haces con `{new_input}`?",
                parse_mode="Markdown",
                reply_markup=_kb_hab_conflict(),
            )
            return HABITO_CONFLICT
        final_value = _accumulate_value(existing, new_input)
        await api.log_habit(date_str, nombre, final_value, user_id)
        extra = f"\n  \\({existing} + {new_input[1:]} = {final_value}\\)" if new_input.startswith("+") and existing else ""
        await msg.reply_text(
            f"✅ *Hábito registrado*\n\n"
            f"  📊 {nombre}: `{final_value}`\n"
            f"  📅 {date_str}{extra}",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await msg.reply_text(
            "⚠️ No pude conectar con la API\\. Asegúrate: `make run-api`",
            parse_mode="Markdown",
        )
    context.user_data.clear()
    return ConversationHandler.END


async def habito_conflict_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query    = update.callback_query
    await query.answer()
    nombre   = context.user_data.get("habito_nombre", "")
    date_str = context.user_data.get("habito_date", str(date.today()))
    user_id  = context.user_data.get("habito_user_id", 0)
    new_val  = context.user_data.get("habito_new_val", "")
    existing = context.user_data.get("habito_existing_val", "")
    if query.data == "hconf_cancel":
        await query.edit_message_text(
            "❌ Operación cancelada\\.",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
        context.user_data.clear()
        return ConversationHandler.END
    final_value = _accumulate_value(existing, f"+{new_val}") if query.data == "hconf_add" else new_val
    try:
        await api.log_habit(date_str, nombre, final_value, user_id)
        op = "sumado" if query.data == "hconf_add" else "sobreescrito"
        await query.edit_message_text(
            f"✅ *{nombre}* {op}: `{existing}` → `{final_value}`",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await query.edit_message_text("⚠️ Error al guardar el hábito.")
    context.user_data.clear()
    return ConversationHandler.END


# ════════════════════════════════════════════════════════════════════════
# EDITAR HÁBITO
# ════════════════════════════════════════════════════════════════════════

def _kb_edit_hab_fields(date_str: str, habit: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Cambiar nombre", callback_data=f"hedit_name_{date_str}_{habit}")],
        [InlineKeyboardButton("📊 Cambiar valor",  callback_data=f"hedit_val_{date_str}_{habit}")],
        [InlineKeyboardButton("← Cancelar",        callback_data=f"habitos_nav_{date_str}")],
    ])


async def cb_hab_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query    = update.callback_query
    await query.answer()
    user_id  = query.from_user.id
    date_str, habit = _parse_hab_callback("he_", query.data)
    context.user_data["edit_hab_date"]    = date_str
    context.user_data["edit_hab_nombre"]  = habit
    context.user_data["edit_hab_user_id"] = user_id
    try:
        habits = await api.get_habits(date_str, user_id)
        valor  = habits.get(habit, "—") if isinstance(habits, dict) else next(
            (h.get("value", "—") for h in habits if h.get("habit") == habit), "—"
        )
    except ApiError:
        valor = "—"
    await query.edit_message_text(
        f"✏️ *Editar hábito*\n\n"
        f"  📊 *{habit}*: `{valor}`\n\n"
        f"¿Qué quieres cambiar?",
        parse_mode="Markdown",
        reply_markup=_kb_edit_hab_fields(date_str, habit),
    )
    return EDIT_HAB_FIELD


async def cb_hab_edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """El usuario elige qué campo editar: nombre o valor."""
    query = update.callback_query
    await query.answer()
    data  = query.data  # hedit_name_{date}_{habit} o hedit_val_{date}_{habit}

    if data.startswith("hedit_name_"):
        rest     = data[len("hedit_name_"):]
        date_str = rest[:10]
        habit    = rest[11:]
        context.user_data["edit_hab_date"]   = date_str
        context.user_data["edit_hab_nombre"] = habit
        await query.edit_message_text(
            f"📝 *Nuevo nombre para '{habit}'*:\n\nEscribe el nuevo nombre:",
            parse_mode="Markdown",
        )
        return EDIT_HAB_NOMBRE

    if data.startswith("hedit_val_"):
        rest     = data[len("hedit_val_"):]
        date_str = rest[:10]
        habit    = rest[11:]
        context.user_data["edit_hab_date"]   = date_str
        context.user_data["edit_hab_nombre"] = habit
        await query.edit_message_text(
            f"📊 *Nuevo valor para '{habit}'*:\n\nEscribe el nuevo valor:",
            parse_mode="Markdown",
        )
        return EDIT_HAB_VALUE

    return ConversationHandler.END


async def cb_hab_edit_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe el nuevo nombre y lo aplica renombrando: borra el viejo + crea el nuevo."""
    nuevo_nombre = update.message.text.strip()
    if not nuevo_nombre:
        await update.message.reply_text("❌ El nombre no puede estar vacío\\.", parse_mode="Markdown")
        return EDIT_HAB_NOMBRE
    return await _do_edit_habit(update, context, new_nombre=nuevo_nombre)


async def cb_hab_edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe el nuevo valor y actualiza el hábito."""
    nuevo_valor = update.message.text.strip()
    if not nuevo_valor:
        await update.message.reply_text("❌ El valor no puede estar vacío\\.", parse_mode="Markdown")
        return EDIT_HAB_VALUE
    return await _do_edit_habit(update, context, new_value=nuevo_valor)


async def _do_edit_habit(
    update: Update, context, new_nombre: str = None, new_value: str = None
) -> int:
    """Aplica la edición del hábito vía API con user_id correcto."""
    date_str      = context.user_data.get("edit_hab_date", "")
    nombre_orig   = context.user_data.get("edit_hab_nombre", "")
    user_id       = context.user_data.get("edit_hab_user_id", update.effective_user.id)
    try:
        if new_nombre and new_nombre != nombre_orig:
            # Renombrar: leer valor actual, borrar, recrear con nuevo nombre
            habits   = await api.get_habits(date_str, user_id)
            valor    = habits.get(nombre_orig) if isinstance(habits, dict) else next(
                (h.get("value") for h in habits if h.get("habit") == nombre_orig), ""
            )
            await api.delete_habit(date_str, nombre_orig, user_id)
            await api.log_habit(date_str, new_nombre, valor or "", user_id)
            msg_txt = f"✅ Hábito renombrado: *{nombre_orig}* → *{new_nombre}*"
        else:
            # Solo actualizar valor
            valor = new_value or ""
            await api.update_habit(date_str, nombre_orig, valor, user_id)
            msg_txt = f"✅ *{nombre_orig}* actualizado a `{valor}`"
        await update.message.reply_text(
            msg_txt,
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await update.message.reply_text(
            "⚠️ No pude conectar con la API\\. Asegúrate: `make run-api`",
            parse_mode="Markdown",
        )
    context.user_data.clear()
    return ConversationHandler.END


# ════════════════════════════════════════════════════════════════════════
# FACTORIES
# ════════════════════════════════════════════════════════════════════════

def build_habito_handler() -> ConversationHandler:
    """ConversationHandler para /habito — registrar un nuevo hábito."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("habito", habito_start),
            CallbackQueryHandler(habito_start_desde_boton, pattern=r"^quick_habito"),
        ],
        states={
            HABITO_NOMBRE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, habito_recv_nombre_text),
            ],
            HABITO_VALUE: [
                CallbackQueryHandler(habito_recv_value_inline, pattern=r"^hval_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, habito_recv_value_text),
            ],
            HABITO_CONFLICT: [
                CallbackQueryHandler(habito_conflict_response, pattern=r"^hconf_"),
            ],
        },
        fallbacks=[CommandHandler("cancelar", _cmd_cancelar_hab)],
        name="nuevo_habito", persistent=False, per_message=False,
    )


def build_edit_hab_handler() -> ConversationHandler:
    """ConversationHandler para editar hábito existente."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_hab_edit_start, pattern=r"^he_")],
        states={
            EDIT_HAB_FIELD: [
                CallbackQueryHandler(cb_hab_edit_field, pattern=r"^hedit_"),
            ],
            EDIT_HAB_NOMBRE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_hab_edit_nombre),
            ],
            EDIT_HAB_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_hab_edit_value),
            ],
        },
        fallbacks=[CommandHandler("cancelar", _cmd_cancelar_hab)],
        name="editar_habito", persistent=False, per_message=False,
    )


async def _cmd_cancelar_hab(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Operación cancelada\\.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Menú", callback_data="menu_home")
        ]]),
    )
    return ConversationHandler.END
