"""
Handlers de configuración de hábitos — /config.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.api_client import ThdoraApiClient
from src.bot.keyboards import HABIT_TYPE_EMOJIS

api = ThdoraApiClient()

# ── Estados ───────────────────────────────────────────────────────────
CFG_NOMBRE, CFG_TYPE, CFG_UNIT, CFG_QUICK = range(40, 44)


async def cmd_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        configs = await api.get_all_habit_configs()
    except Exception:
        configs = []
    if configs:
        lines = ["⚙️ *Configuración de hábitos:*\n"]
        for c in configs:
            emoji = HABIT_TYPE_EMOJIS.get(c["habit_type"], "📝")
            unit  = f" ({c['unit']})" if c.get("unit") else ""
            quick = ", ".join(c["quick_vals"]) if c.get("quick_vals") else "texto libre"
            lines.append(f"  {emoji} *{c['name']}*{unit} — {c['habit_type']}\n     Botones: {quick}")
        text = "\n".join(lines)
    else:
        text = "⚙️ No hay ningún hábito configurado todavía\\."
    await update.message.reply_text(
        text + "\n\n➕ Escribe el nombre del hábito a configurar:",
        parse_mode="Markdown",
    )
    return CFG_NOMBRE


async def cfg_recv_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("❌ El nombre no puede estar vacío.")
        return CFG_NOMBRE
    context.user_data["cfg_nombre"] = nombre
    await update.message.reply_text(
        f"⚙️ Configurando: *{nombre}*\n\n¿Qué tipo de hábito es?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔢 Numérico", callback_data="cfgt_numeric"),
            InlineKeyboardButton("⏱️ Tiempo",   callback_data="cfgt_time"),
        ], [
            InlineKeyboardButton("✅ Sí/No",    callback_data="cfgt_boolean"),
            InlineKeyboardButton("📝 Texto",    callback_data="cfgt_text"),
        ]]),
    )
    return CFG_TYPE


async def cfg_recv_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    habit_type = query.data.replace("cfgt_", "")
    context.user_data["cfg_type"] = habit_type
    if habit_type == "boolean":
        await _save_habit_config(query.message, context, None, None)
        return ConversationHandler.END
    await query.edit_message_text(
        f"✅ Tipo: *{habit_type}*\n\n¿Unidad? \\(ej: `h`, `min`, `L`\\) o /skip:",
        parse_mode="Markdown",
    )
    return CFG_UNIT


async def cfg_recv_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data["cfg_unit"] = None if text.lower() == "/skip" else text
    await update.message.reply_text(
        "🚀 Botones rápidos: valores separados por comas \\(ej: `6h,7h,8h`\\) o /skip:"
    )
    return CFG_QUICK


async def cfg_recv_quick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    quick_vals = None
    if text.lower() != "/skip" and text:
        quick_vals = [v.strip() for v in text.split(",") if v.strip()]
    await _save_habit_config(update.message, context, context.user_data.get("cfg_unit"), quick_vals)
    return ConversationHandler.END


async def _save_habit_config(msg, context, unit, quick_vals) -> None:
    nombre     = context.user_data.get("cfg_nombre", "")
    habit_type = context.user_data.get("cfg_type", "text")
    try:
        await api.upsert_habit_config(name=nombre, habit_type=habit_type, unit=unit, quick_vals=quick_vals)
        quick_str = ", ".join(quick_vals) if quick_vals else "texto libre"
        await msg.reply_text(
            f"✅ *{nombre}* configurado:\n  Tipo: {habit_type}  Unidad: {unit or '—'}\n  Botones: {quick_str}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await msg.reply_text(f"⚠️ Error al guardar la config: {e}")
    context.user_data.clear()


def build_config_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("config", cmd_config)],
        states={
            CFG_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_nombre)],
            CFG_TYPE:   [CallbackQueryHandler(cfg_recv_type, pattern=r"^cfgt_")],
            CFG_UNIT: [
                CommandHandler("skip", lambda u, c: cfg_recv_unit(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_unit),
            ],
            CFG_QUICK: [
                CommandHandler("skip", lambda u, c: cfg_recv_quick(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_quick),
            ],
        },
        fallbacks=[CommandHandler("cancelar", _cmd_cancelar_cfg)],
        name="config_habito", persistent=False, per_message=False,
    )


async def _cmd_cancelar_cfg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Operación cancelada\\.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Menú", callback_data="menu_home")
        ]]),
    )
    return ConversationHandler.END
