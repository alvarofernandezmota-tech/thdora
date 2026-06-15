# src/bot/handlers/commands.py
import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.bot.api_client import ThdoraApiClient
from src.bot.keyboards import _kb_start

logger = logging.getLogger(__name__)
api = ThdoraApiClient()

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await update.message.reply_text(
        "🌟 *THDORA* — Tu asistente personal de hábitos y citas\n\n"
        "📅 */citas* — Ver citas de hoy\n"
        "➕ */nueva* — Crear nueva cita\n"
        "🗑️ */borrar* — Borrar cita\n"
        "📊 */habito* — Registrar hábito\n"
        "📈 */diario* — Resumen del día\n"
        "📆 */semana* — Resumen semanal\n\n"
        "O escríbeme directamente: *mañana dentista a las 10*",
        parse_mode="Markdown",
        reply_markup=_kb_start()
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await cmd_start(update, context)

async def cmd_citas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    today = date.today().isoformat()
    try:
        appointments = await api.get_appointments(today, user_id=user_id)
        if not appointments:
            await update.message.reply_text(
                f"📅 *Hoy {today} no tienes citas*\n\n"
                "Usa */nueva* para añadir una",
                parse_mode="Markdown",
                reply_markup=_kb_start()
            )
            return

        text = f"📅 *Citas de hoy {today}*\n\n"
        for i, apt in enumerate(appointments, 1):
            text += f"{i}. *{apt['time']}* — {apt['name']} ({apt['type']})"
            if apt.get("notes"):
                text += f"\n   _{apt['notes']}_"
            text += "\n"
        text += "\nUsa */borrar* para eliminar una"
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=_kb_start())
    except Exception as e:
        logger.error(f"Error en /citas: {e}")
        await update.message.reply_text("❌ Error al obtener citas", reply_markup=_kb_start())

async def cmd_nueva(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    today = date.today().isoformat()
    try:
        text = update.message.text or ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        if not args:
            await update.message.reply_text(
                "📝 *Nueva cita*\n\n"
                "Formato: */nueva hora nombre tipo [notas]*\n"
                "Ejemplo: */nueva 10:00 Dentista médica Revisión anual*\n\n"
                "Tipos: médica, personal, trabajo, otra",
                parse_mode="Markdown",
                reply_markup=_kb_start()
            )
            return

        time = args[0] if len(args) > 0 else "09:00"
        name = args[1] if len(args) > 1 else "Cita"
        apt_type = args[2] if len(args) > 2 else "otra"
        notes = " ".join(args[3:]) if len(args) > 3 else ""

        conflict = await api.check_appointment_conflict(today, time, user_id=user_id)
        if conflict:
            await update.message.reply_text(
                f"⚠️ *{time}* ya está ocupada con *{conflict['name']}*\n"
                f"Elige otra hora",
                parse_mode="Markdown",
                reply_markup=_kb_start()
            )
            return

        await api.create_appointment(today, time, name, apt_type, notes, user_id=user_id)
        await update.message.reply_text(
            f"✅ *{name}* añadida hoy a las *{time}*",
            parse_mode="Markdown",
            reply_markup=_kb_start()
        )
    except Exception as e:
        logger.error(f"Error en /nueva: {e}")
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=_kb_start())

async def cmd_borrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    today = date.today().isoformat()
    try:
        text = update.message.text or ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        if not args:
            appointments = await api.get_appointments(today, user_id=user_id)
            if not appointments:
                await update.message.reply_text("No hay citas hoy", reply_markup=_kb_start())
                return

            buttons = []
            for apt in appointments:
                btn = InlineKeyboardButton(
                    f"{apt['time']} — {apt['name']}",
                    callback_data=f"del_apt|{apt['index']}"
                )
                buttons.append([btn])
            buttons.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel")])
            await update.message.reply_text(
                "🗑️ *¿Qué cita quieres borrar?*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        index = int(args[0]) if args[0].isdigit() else -1
        if index <= 0:
            await update.message.reply_text("⚠️ Índice inválido", reply_markup=_kb_start())
            return

        ok = await api.delete_appointment(today, index, user_id=user_id)
        if ok:
            await update.message.reply_text("✅ Cita eliminada", reply_markup=_kb_start())
        else:
            await update.message.reply_text("⚠️ Cita no encontrada", reply_markup=_kb_start())
    except Exception as e:
        logger.error(f"Error en /borrar: {e}")
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=_kb_start())

async def cmd_habito(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    today = date.today().isoformat()
    try:
        text = update.message.text or ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        if not args:
            habits = await api.get_habits(today, user_id=user_id)
            if not habits:
                await update.message.reply_text("No hay hábitos registrados hoy", reply_markup=_kb_start())
                return

            text = "📊 *Hábitos de hoy*\n\n"
            for habit, value in habits.items():
                text += f"• *{habit}*: {value}\n"
            await update.message.reply_text(text, parse_mode="Markdown", reply_markup=_kb_start())
            return

        habit_name = args[0]
        habit_value = " ".join(args[1:]) if len(args) > 1 else ""

        if not habit_value:
            await update.message.reply_text(
                "📝 *Registro de hábito*\n\n"
                "Formato: */habito nombre valor*\n"
                "Ejemplo: */habito sueño 8h*",
                parse_mode="Markdown",
                reply_markup=_kb_start()
            )
            return

        await api.log_habit(today, habit_name, habit_value, user_id=user_id)
        await update.message.reply_text(
            f"✅ *{habit_name}*: {habit_value} registrado",
            parse_mode="Markdown",
            reply_markup=_kb_start()
        )
    except Exception as e:
        logger.error(f"Error en /habito: {e}")
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=_kb_start())

async def cmd_diario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    today = date.today().isoformat()
    try:
        summary = await api.get_summary(today, user_id=user_id)
        appointments = summary.get("appointments", [])
        habits = summary.get("habits", {})

        text = f"📅 *Resumen del día {today}*\n\n"

        if appointments:
            text += "📅 *Citas*\n"
            for apt in appointments:
                text += f"• {apt['time']} — {apt['name']} ({apt['type']})\n"
        else:
            text += "📅 *Sin citas hoy*\n"

        text += "\n"

        if habits:
            text += "📊 *Hábitos*\n"
            for habit, value in habits.items():
                text += f"• *{habit}*: {value}\n"
        else:
            text += "📊 *Sin hábitos registrados*\n"

        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=_kb_start())
    except Exception as e:
        logger.error(f"Error en /diario: {e}")
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=_kb_start())

async def cmd_semana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    today = date.today().isoformat()
    try:
        week_summary = await api.get_week_summary(today, user_id=user_id)

        text = f"📆 *Resumen semanal*\n\n"
        for day, data in sorted(week_summary.items()):
            appointments = data.get("appointments", [])
            habits = data.get("habits", {})

            if appointments or habits:
                text += f"📅 *{day}*\n"
                for apt in appointments:
                    text += f"  • {apt['time']} — {apt['name']}\n"
                for habit, value in habits.items():
                    text += f"  • {habit}: {value}\n"
                text += "\n"

        if text == f"📆 *Resumen semanal*\n\n":
            text += "No hay datos esta semana"

        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=_kb_start())
    except Exception as e:
        logger.error(f"Error en /semana: {e}")
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=_kb_start())
