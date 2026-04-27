"""
Handlers de hábitos: /habitos, /habito, borrar, editar, sumar.

Flujo /habito (build_habito_handler):
    HABITO_NOMBRE   → nombre del hábito (texto)
    HABITO_VALUE    → valor (botones quick_vals si hay config, o texto)
    HABITO_CONFLICT → si ya existe valor hoy: sobreescribir / sumar / cancelar

Flujo editar hábito (build_edit_hab_handler):
    Entrada: callback he_{date_str}_{habit}
    EDIT_HAB_FIELD  → botones: cambiar nombre / cambiar valor / cancelar
    EDIT_HAB_NOMBRE → nuevo nombre (texto)
    EDIT_HAB_VALUE  → nuevo valor (botones o texto)

Flujo sumar a hábito (cb_hab_add / cb_hab_add_value):
    Entrada: callback ha_{date_str}_{habit}
    El usuario escribe el incremento (+N) o nuevo valor directo.
    Se resuelve fuera de ConversationHandler (acum context).

Nota sobre callback_data con fechas:
    Los prefijos hd_, hdc_, he_, ha_ usan {prefix}{date_str}_{habit}.
    La fecha contiene guiones (2026-04-13), así que NO usar split('_', 2).
    Se extrae con: data[len(prefix):] y luego split('_', 1) ya que
    date_str siempre tiene formato fijo YYYY-MM-DD (10 caracteres).

Fixes v0.16.2 (2026-04-27):
    - B-NEW3: eliminado habit[:15] en _kb_edit_hab_fields — los hábitos con
      nombre > 15 chars fallaban en edición porque la API no los encontraba
      con el nombre truncado. Ahora se usa el nombre completo igual que en
      _kb_hab_actions y _kb_hab_confirm (que ya tenían este fix documentado
      como FIX B3).
"""

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
    """
    Extrae (date_str, habit) de un callback_data con formato:
        {prefix}{date_str}_{habit}
    Ejemplo: 'hd_2026-04-13_Agua' con prefix='hd_' → ('2026-04-13', 'Agua')

    La fecha tiene formato fijo YYYY-MM-DD (10 chars), así que
    usamos slice directo en vez de split para evitar romper con
    nombres de hábitos que contengan guiones bajos.
    """
    rest     = data[len(prefix):]   # '2026-04-13_Agua'
    date_str = rest[:10]            # '2026-04-13'
    habit    = rest[11:]            # 'Agua' (salta el '_' del índice 10)
    return date_str, habit


# ════════════════════════════════════════════════════════════════════════
# VISTAS
# ════════════════════════════════════════════════════════════════════════

async def cmd_habitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clean_acum_context(context)
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    await _show_habitos(update.message, date_str)


async def _show_habitos(msg, date_str: str) -> None:
    try:
        habits = await api.get_habits(date_str)
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
    for h, v in habits.items():
        await msg.reply_text(
            f"• *{h}*: `{v}`",
            parse_mode="Markdown",
            reply_markup=_kb_hab_actions(date_str, h),
        )


async def cb_habitos_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str = query.data.replace("habitos_nav_", "")
    await _show_habitos(query.message, date_str)


# ════════════════════════════════════════════════════════════════════════
# BORRAR / SUMAR
# ════════════════════════════════════════════════════════════════════════

async def cb_hab_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str, habit = _parse_hab_callback("hd_", query.data)
    await query.edit_message_reply_markup(reply_markup=_kb_hab_confirm(date_str, habit))


async def cb_hab_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str, habit = _parse_hab_callback("hdc_", query.data)
    try:
        ok  = await api.delete_habit(date_str, habit)
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
    context.user_data["acum_hab_date"]   = date_str
    context.user_data["acum_hab_nombre"] = habit
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
    if not date_str or not habit:
        return
    try:
        habits      = await api.get_habits(date_str)
        existing    = habits.get(habit)
        final_value = _accumulate_value(existing, new_input)
        await api.log_habit(date_str, habit, final_value)
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
    context.user_data["habito_date"] = str(date.today())
    fecha_label = _date_short(str(date.today()))
    await update.message.reply_text(
        f"📊 *Nuevo hábito para {fecha_label}*\n\n✏️ *Paso 1/2* — ¿Cómo se llama el hábito?",
        parse_mode="Markdown",
    )
    return HABITO_NOMBRE


async def habito_start_desde_boton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    data = query.data
    if data.startswith("quick_habito_"):
        fecha = data.replace("quick_habito_", "")
    else:
        fecha = str(date.today())
    context.user_data["habito_date"] = fecha
    fecha_label = _date_short(fecha)
    await query.message.reply_text(
        f"📊 *Nuevo hábito para {fecha_label}*\n\n✏️ *Paso 1/2* — ¿Cómo se llama el hábito?",
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
    try:
        cfg = await api.get_habit_config(nombre)
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
    try:
        habits   = await api.get_habits(date_str)
        existing = habits.get(nombre)
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
        await api.log_habit(date_str, nombre, final_value)
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
        await api.log_habit(date_str, nombre, final_value)
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
    """Teclado para elegir qué campo del hábito editar.

    FIX B-NEW3 (v0.16.2): eliminado habit[:15] — el nombre completo es
    necesario para que _parse_hab_callback y la API lo encuentren.
    Los callbacks hedit_name_ y hedit_val_ usan ahora el nombre sin truncar,
    igual que _kb_hab_actions y _kb_hab_confirm (FIX B3 anterior).
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Cambiar nombre", callback_data=f"hedit_name_{date_str}_{habit}")],
        [InlineKeyboardButton("📊 Cambiar valor",  callback_data=f"hedit_val_{date_str}_{habit}")],
        [InlineKeyboardButton("← Cancelar",        callback_data=f"habitos_nav_{date_str}")],
    ])


async def cb_hab_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    date_str, habit = _parse_hab_callback("he_", query.data)
    context.user_data["edit_hab_date"]   = date_str
    context.user_data["edit_hab_nombre"] = habit
    try:
        habits = await api.get_habits(date_str)
        valor  = habits.get(habit, "—")
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
    """El usuario eligió cambiar nombre o valor."""
    query = update.callback_query
    await query.answer()
    data  = query.data  # hedit_{field}_{date_str}_{habit}
    rest  = data[len("hedit_"):]
    field, rest2 = rest.split("_", 1)
    # date_str = primeros 10 chars de rest2 (formato YYYY-MM-DD fijo)
    date_str = rest2[:10]
    habit    = rest2[11:]
    context.user_data["edit_hab_field"]  = field
    context.user_data["edit_hab_date"]   = date_str
    context.user_data["edit_hab_nombre"] = habit

    if field == "name":
        await query.edit_message_text(
            f"📝 *Nuevo nombre* para *{habit}*:",
            parse_mode="Markdown",
        )
        return EDIT_HAB_NOMBRE
    elif field == "val":
        try:
            cfg = await api.get_habit_config(habit)
        except Exception:
            cfg = None
        kb = _kb_hab_value(cfg)
        if kb:
            await query.edit_message_text(
                f"📊 *Nuevo valor* para *{habit}*:",
                parse_mode="Markdown",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(
                f"📊 *Nuevo valor* para *{habit}* \\(ej: `8h`, `30min`, `2L`\\):",
                parse_mode="Markdown",
            )
        return EDIT_HAB_VALUE
    return ConversationHandler.END


async def cb_hab_edit_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nuevo = update.message.text.strip()
    if not nuevo:
        await update.message.reply_text("❌ El nombre no puede estar vacío\\.", parse_mode="Markdown")
        return EDIT_HAB_NOMBRE
    context.user_data["edit_hab_nombre_nuevo"] = nuevo
    return await _do_edit_habit(update.message, context, None)


async def cb_hab_edit_value_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.replace("hval_", "")
    if value == "__otro":
        await query.edit_message_text("✏️ Escribe el nuevo valor:")
        return EDIT_HAB_VALUE
    return await _do_edit_habit(query.message, context, value)


async def cb_hab_edit_value_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _do_edit_habit(update.message, context, update.message.text.strip())


async def _do_edit_habit(msg, context, value: Optional[str]) -> int:
    date_str     = context.user_data.get("edit_hab_date", "")
    nombre_orig  = context.user_data.get("edit_hab_nombre", "")
    nombre_nuevo = context.user_data.get("edit_hab_nombre_nuevo", nombre_orig)
    try:
        if nombre_nuevo != nombre_orig:
            habits    = await api.get_habits(date_str)
            val_orig  = habits.get(nombre_orig)
            final_val = value if value else val_orig
            await api.delete_habit(date_str, nombre_orig)
            await api.log_habit(date_str, nombre_nuevo, final_val or "")
        else:
            if value:
                await api.update_habit(date_str, nombre_orig, value)
            final_val = value or "sin cambios"
        cambios = []
        if nombre_nuevo != nombre_orig:
            cambios.append(f"  📝 Nombre: *{nombre_orig}* → *{nombre_nuevo}*")
        if value:
            cambios.append(f"  📊 Valor: `{final_val}`")
        if not cambios:
            cambios.append("  _Sin cambios_")
        await msg.reply_text(
            f"✅ *Hábito actualizado*\n\n" + "\n".join(cambios),
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await msg.reply_text("⚠️ Error al actualizar el hábito.")
    context.user_data.clear()
    return ConversationHandler.END


# ════════════════════════════════════════════════════════════════════════
# FACTORIES
# ════════════════════════════════════════════════════════════════════════

def build_habito_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("habito", habito_start),
            CallbackQueryHandler(habito_start_desde_boton, pattern=r"^quick_habito"),
        ],
        states={
            HABITO_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, habito_recv_nombre_text)],
            HABITO_VALUE: [
                CallbackQueryHandler(habito_recv_value_inline, pattern=r"^hval_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, habito_recv_value_text),
            ],
            HABITO_CONFLICT: [CallbackQueryHandler(habito_conflict_response, pattern=r"^hconf_")],
        },
        fallbacks=[CommandHandler("cancelar", _cmd_cancelar_hab)],
        name="registrar_habito", persistent=False, per_message=False,
    )


def build_edit_hab_handler() -> ConversationHandler:
    """
    ConversationHandler para editar un hábito.

    Entrada: callback he_{date_str}_{habit}
    Estados:
        EDIT_HAB_FIELD  → botones: cambiar nombre / cambiar valor
        EDIT_HAB_NOMBRE → nuevo nombre (texto)
        EDIT_HAB_VALUE  → nuevo valor (botones quick_vals o texto)
    """
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
                CallbackQueryHandler(cb_hab_edit_value_inline, pattern=r"^hval_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_hab_edit_value_text),
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
