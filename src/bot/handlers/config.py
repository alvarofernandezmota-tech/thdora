"""
Handlers de configuración — /config.

Estructura del ConversationHandler:
    CFG_MENU       → menú raíz: Hábitos | Notificaciones
    └─ Rama Hábitos:
        CFG_NOMBRE     → nombre del hábito a configurar (texto)
        CFG_TYPE       → tipo: numeric / time / boolean / text (botones)
        CFG_UNIT       → unidad (texto o skip)
        CFG_QUICK      → botones rápidos separados por comas (texto o skip)
        CFG_DEL_CONF   → confirmación antes de borrar una config
    └─ Rama Notificaciones:
        NOTIF_MENU        → menú con toggles + botones de hora/offsets
        NOTIF_SET_TIME    → teclado de horas para resumen o evening log
                            Botón ❌ Cancelar → vuelve a NOTIF_MENU sin guardar
        NOTIF_SET_OFFSETS → teclado de minutos antes de cita
                            Botón ❌ Cancelar → vuelve a NOTIF_MENU sin guardar

Nota scheduler:
    Solo se reprograman los jobs diarios cuando el usuario confirma
    una nueva hora (notif_recv_time). Los toggles on/off NO reprograman
    para evitar jobs duplicados.

Nota /skip:
    Se acepta '/skip' (con barra) y 'skip' (sin barra) en CFG_UNIT y CFG_QUICK.
"""

import asyncio
import logging

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
from src.bot.keyboards import (
    HABIT_TYPE_EMOJIS,
    _kb_config_menu,
    _kb_notif_menu,
    _kb_notif_hora,
    _kb_notif_offsets,
)
from src.bot.scheduler import schedule_user_jobs

logger = logging.getLogger(__name__)
api    = ThdoraApiClient()

# ── Estados ────────────────────────────────────────────────
CFG_MENU, CFG_NOMBRE, CFG_TYPE, CFG_UNIT, CFG_QUICK = range(40, 45)
NOTIF_MENU, NOTIF_SET_TIME, NOTIF_SET_OFFSETS = range(45, 48)
CFG_DEL_CONF = 48


def _is_skip(text: str) -> bool:
    """Acepta '/skip' y 'skip' (con y sin barra)."""
    return text.lower().strip().lstrip("/") == "skip"


# ── Entrada /config ──────────────────────────────────────────

async def cmd_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point de /config y del botón quick_config del menú."""
    msg = update.message or (update.callback_query and update.callback_query.message)
    if update.callback_query:
        await update.callback_query.answer()
    await msg.reply_text(
        "⚙️ *Configuración*\n\n¿Qué quieres configurar?",
        parse_mode="Markdown",
        reply_markup=_kb_config_menu(),
    )
    return CFG_MENU


async def cfg_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ramifica según la elección del menú raíz."""
    query = update.callback_query
    await query.answer()
    if query.data == "cfg_habitos":
        return await _show_hab_configs(query)
    if query.data == "cfg_notif":
        return await _show_notif_menu(query, context)
    if query.data == "cfg_back_menu":
        await query.edit_message_text(
            "⚙️ *Configuración*\n\n¿Qué quieres configurar?",
            parse_mode="Markdown",
            reply_markup=_kb_config_menu(),
        )
        return CFG_MENU
    return CFG_MENU


async def _show_hab_configs(query) -> int:
    """Muestra la lista de hábitos configurados con botón borrar por cada uno."""
    try:
        configs = await asyncio.wait_for(api.get_all_habit_configs(), timeout=5.0)
    except asyncio.TimeoutError:
        configs = []
    except Exception:
        configs = []
    lines, buttons = [], []
    if configs:
        lines.append("⚙️ *Hábitos configurados:*\n")
        for c in configs:
            emoji = HABIT_TYPE_EMOJIS.get(c["habit_type"], "📝")
            unit  = f" ({c['unit']})" if c.get("unit") else ""
            quick = ", ".join(c["quick_vals"]) if c.get("quick_vals") else "texto libre"
            lines.append(f"  {emoji} *{c['name']}*{unit} — {c['habit_type']}\n     Botones: {quick}")
            buttons.append([
                InlineKeyboardButton(f"🗑️ Borrar {c['name']}", callback_data=f"cfgdel_{c['name'][:20]}")
            ])
    else:
        lines.append("⚙️ No hay ningún hábito configurado todavía\\.")
    buttons.append([InlineKeyboardButton("← Volver", callback_data="cfg_back_menu")])
    await query.edit_message_text(
        "\n".join(lines) + "\n\n➕ Escribe el nombre del hábito a configurar:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return CFG_NOMBRE


# ── Borrar config de hábito ──────────────────────────────────

async def cfg_del_hab(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    nombre = query.data[len("cfgdel_"):]
    context.user_data["cfg_del_nombre"] = nombre
    await query.edit_message_text(
        f"⚠️ ¿Borrar la config de *{nombre}*?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Sí, borrar", callback_data="cfgdelok"),
            InlineKeyboardButton("❌ Cancelar",  callback_data="cfg_habitos"),
        ]]),
    )
    return CFG_DEL_CONF


async def cfg_del_hab_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    nombre = context.user_data.get("cfg_del_nombre", "")
    try:
        await api.delete_habit_config(nombre)
        await query.edit_message_text(
            f"🗑️ Config de *{nombre}* eliminada\\.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("← Volver", callback_data="cfg_back_menu")
            ]]),
        )
    except Exception as e:
        await query.edit_message_text(f"⚠️ Error al borrar: {e}")
    context.user_data.pop("cfg_del_nombre", None)
    return CFG_MENU


# ── Rama Hábitos ────────────────────────────────────────────

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
        f"✅ Tipo: *{habit_type}*\n\n¿Unidad? \\(ej: `h`, `min`, `L`\\) o escribe `skip` para omitir:",
        parse_mode="Markdown",
    )
    return CFG_UNIT


async def cfg_recv_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data["cfg_unit"] = None if _is_skip(text) else text
    await update.message.reply_text(
        "🚀 Botones rápidos: valores separados por comas \\(ej: `6h,7h,8h`\\)\nO escribe `skip` para omitir:",
        parse_mode="Markdown",
    )
    return CFG_QUICK


async def cfg_recv_quick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    quick_vals = None
    if not _is_skip(text):
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


# ── Rama Notificaciones ────────────────────────────────────────

async def _show_notif_menu(query, context) -> int:
    user_id = str(query.from_user.id)
    try:
        cfg = await api.get_user_config(user_id)
    except Exception:
        cfg = {}
    context.user_data["notif_cfg"] = cfg
    await query.edit_message_text(
        "🔔 *Notificaciones*\n\nPulsa un botón para activar/desactivar o cambiar la hora:",
        parse_mode="Markdown",
        reply_markup=_kb_notif_menu(cfg),
    )
    return NOTIF_MENU


async def notif_menu_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gestiona toggles y navegación del menú de notificaciones.
    NOTA: los toggles solo guardan en la API, NO reprograman el scheduler.
    Los jobs solo se reprograman cuando el usuario cambia la hora real.
    """
    query   = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    cfg     = context.user_data.get("notif_cfg", {})
    data    = query.data

    if data == "notif_toggle_summary":
        new_val = not cfg.get("daily_summary_enabled", True)
        cfg = await api.update_user_config(user_id, daily_summary_enabled=new_val)
        context.user_data["notif_cfg"] = cfg
        await query.edit_message_reply_markup(_kb_notif_menu(cfg))
        return NOTIF_MENU

    if data == "notif_toggle_aviso":
        new_val = not cfg.get("notif_enabled", True)
        cfg = await api.update_user_config(user_id, notif_enabled=new_val)
        context.user_data["notif_cfg"] = cfg
        await query.edit_message_reply_markup(_kb_notif_menu(cfg))
        return NOTIF_MENU

    if data == "notif_toggle_evening":
        new_val = not cfg.get("evening_log_enabled", True)
        cfg = await api.update_user_config(user_id, evening_log_enabled=new_val)
        context.user_data["notif_cfg"] = cfg
        await query.edit_message_reply_markup(_kb_notif_menu(cfg))
        return NOTIF_MENU

    if data == "notif_set_summary_time":
        context.user_data["notif_set_which"] = "summary"
        await query.edit_message_text(
            "⏰ ¿A qué hora quieres el *resumen diario*?",
            parse_mode="Markdown",
            reply_markup=_kb_notif_hora(),
        )
        return NOTIF_SET_TIME

    if data == "notif_set_evening_time":
        context.user_data["notif_set_which"] = "evening"
        await query.edit_message_text(
            "⏰ ¿A qué hora quieres el *evening log*?",
            parse_mode="Markdown",
            reply_markup=_kb_notif_hora(),
        )
        return NOTIF_SET_TIME

    if data == "notif_set_offsets":
        await query.edit_message_text(
            "⏰ ¿Cuántos minutos antes quieres que te avise de cada cita?",
            reply_markup=_kb_notif_offsets(),
        )
        return NOTIF_SET_OFFSETS

    if data == "cfg_back_menu":
        await query.edit_message_text(
            "⚙️ *Configuración*\n\n¿Qué quieres configurar?",
            parse_mode="Markdown",
            reply_markup=_kb_config_menu(),
        )
        return CFG_MENU

    return NOTIF_MENU


async def notif_cancel_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Maneja el botón ❌ Cancelar de los teclados _kb_notif_hora y _kb_notif_offsets.
    callback_data='cfg_notif' → recarga el menú de notificaciones sin guardar nada.
    """
    query = update.callback_query
    await query.answer()
    return await _show_notif_menu(query, context)


async def notif_recv_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda la hora elegida y reprograma el job diario correspondiente."""
    query   = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    hora    = query.data.replace("notif_hora_", "")   # "08:00"
    which   = context.user_data.get("notif_set_which", "summary")
    if which == "summary":
        cfg = await api.update_user_config(user_id, daily_summary_time=hora)
    else:
        cfg = await api.update_user_config(user_id, evening_log_time=hora)
    context.user_data["notif_cfg"] = cfg
    # Reprogramar jobs solo cuando cambia la hora real
    # FIX: usar context.bot en vez de query.get_bot() (deprecated en PTB v20+)
    try:
        schedule_user_jobs(context.bot, user_id, cfg)
    except Exception as e:
        logger.warning("No se pudieron reprogramar jobs para %s: %s", user_id, e)
    tipo_str = "resumen diario" if which == "summary" else "evening log"
    await query.edit_message_text(
        f"✅ *{tipo_str}* a las *{hora}*\n\n🔔 *Notificaciones*",
        parse_mode="Markdown",
        reply_markup=_kb_notif_menu(cfg),
    )
    return NOTIF_MENU


async def notif_recv_offsets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda los minutos antes de cita elegidos."""
    query   = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    raw     = query.data.replace("notif_offsets_", "")  # "15,30,60"
    offsets = raw.split(",")
    cfg = await api.update_user_config(user_id, notif_offsets=offsets)
    context.user_data["notif_cfg"] = cfg
    label = " + ".join(f"{o} min" for o in offsets)
    await query.edit_message_text(
        f"✅ Avisos: *{label}* antes de cada cita\n\n🔔 *Notificaciones*",
        parse_mode="Markdown",
        reply_markup=_kb_notif_menu(cfg),
    )
    return NOTIF_MENU


# ── Cancelar flujo completo ─────────────────────────────────────

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


# ── ConversationHandler ────────────────────────────────────────

def build_config_handler() -> ConversationHandler:
    """
    ConversationHandler de configuración.

    Entry points:
        /config        → cmd_config
        ^quick_config$ → cmd_config (botón ⚙️ del menú principal)

    IMPORTANTE: quick_config NO debe registrarse como handler global
    en main.py porque es entry_point aquí — habría conflicto de captura.
    """
    return ConversationHandler(
        entry_points=[
            CommandHandler("config", cmd_config),
            CallbackQueryHandler(cmd_config, pattern=r"^quick_config$"),
        ],
        states={
            CFG_MENU: [
                CallbackQueryHandler(cfg_menu_choice, pattern=r"^(cfg_habitos|cfg_notif|cfg_back_menu)$"),
            ],
            CFG_NOMBRE: [
                CallbackQueryHandler(cfg_del_hab,     pattern=r"^cfgdel_"),
                CallbackQueryHandler(cfg_menu_choice, pattern=r"^cfg_back_menu$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_nombre),
            ],
            CFG_DEL_CONF: [
                CallbackQueryHandler(cfg_del_hab_confirm, pattern=r"^cfgdelok$"),
                CallbackQueryHandler(cfg_menu_choice,     pattern=r"^cfg_habitos$"),
            ],
            CFG_TYPE: [
                CallbackQueryHandler(cfg_recv_type, pattern=r"^cfgt_"),
            ],
            CFG_UNIT: [
                CommandHandler("skip", cfg_recv_unit),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_unit),
            ],
            CFG_QUICK: [
                CommandHandler("skip", cfg_recv_quick),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_quick),
            ],
            NOTIF_MENU: [
                CallbackQueryHandler(
                    notif_menu_action,
                    pattern=r"^(notif_toggle_|notif_set_|cfg_back_menu)"
                ),
            ],
            NOTIF_SET_TIME: [
                # Botón ❌ Cancelar del teclado de horas → vuelve al menú sin guardar
                CallbackQueryHandler(notif_cancel_to_menu, pattern=r"^cfg_notif$"),
                CallbackQueryHandler(notif_recv_time,      pattern=r"^notif_hora_"),
            ],
            NOTIF_SET_OFFSETS: [
                # Botón ❌ Cancelar del teclado de offsets → vuelve al menú sin guardar
                CallbackQueryHandler(notif_cancel_to_menu, pattern=r"^cfg_notif$"),
                CallbackQueryHandler(notif_recv_offsets,   pattern=r"^notif_offsets_"),
            ],
        },
        fallbacks=[CommandHandler("cancelar", _cmd_cancelar_cfg)],
        name="config", persistent=False, per_message=False,
    )
