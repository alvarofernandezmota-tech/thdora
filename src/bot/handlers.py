# src/bot/handlers.py
from telegram import Update
from telegram.ext import ContextTypes
from src.bot.api_client import get_summary, get_appointments, create_appointment, log_habit


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hola! Soy THDORA.\n\n"
        "Comandos disponibles:\n"
        "/hoy — resumen del día\n"
        "/citas — ver citas\n"
        "/cita — nueva cita\n"
        "/habito — registrar hábito\n"
        "/resumen — resumen completo"
    )


async def cmd_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = await get_summary()
        citas = data.get('appointments', [])
        habitos = data.get('habits', {})
        fecha = data.get('date', '')

        texto = f"📅 Resumen del {fecha}\n\n"

        texto += "🗓 Citas:\n"
        if citas:
            for c in citas:
                texto += f"  • {c}\n"
        else:
            texto += "  Sin citas hoy\n"

        texto += "\n💪 Hábitos:\n"
        if habitos:
            for nombre, valor in habitos.items():
                texto += f"  • {nombre}: {valor}\n"
        else:
            texto += "  Sin hábitos registrados\n"

        await update.message.reply_text(texto)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_citas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        citas = await get_appointments()
        if not citas:
            await update.message.reply_text("📭 No hay citas registradas.")
            return
        texto = "\n".join([f"• {c}" for c in citas])
        await update.message.reply_text(f"📋 Citas:\n{texto}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_cita(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args:
        await update.message.reply_text(
            "📝 Uso: /cita HH:MM descripción\n"
            "Ej: /cita 10:30 Médico"
        )
        return
    try:
        hora = args[0]
        descripcion = " ".join(args[1:]) if len(args) > 1 else "Sin descripción"
        data = {"time": hora, "description": descripcion}
        result = await create_appointment(data)
        await update.message.reply_text(f"✅ Cita creada: {hora} — {descripcion}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_habito(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args:
        await update.message.reply_text("Uso: /habito nombre valor\nEj: /habito agua 2")
        return
    try:
        data = {"nombre": args[0], "valor": args[1] if len(args) > 1 else "1"}
        result = await log_habit(data)
        await update.message.reply_text(f"✅ Hábito registrado: {result}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await cmd_hoy(update, context)
