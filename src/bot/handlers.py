# src/bot/handlers.py
from telegram import Update
from telegram.ext import ContextTypes
from src.bot.api_client import (
    get_summary, get_appointments, create_appointment,
    log_habit, get_habits, delete_appointment
)

TIPOS_VALIDOS = {"médica", "personal", "trabajo", "otra"}
TIPOS_TEXTO = "médica | personal | trabajo | otra"


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hola! Soy THDORA.\n\n"
        "Comandos disponibles:\n"
        "/hoy — resumen del día\n"
        "/citas — ver citas de hoy\n"
        "/cita — nueva cita\n"
        "/borrar_cita — eliminar cita\n"
        "/habitos — ver hábitos de hoy\n"
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
            for i, c in enumerate(citas):
                texto += f"  [{i}] {c.get('time', '')} — {c.get('type', '')}\n"
                if c.get('notes'):
                    texto += f"    💬 {c['notes']}\n"
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
            await update.message.reply_text("📭 No hay citas hoy.")
            return
        texto = "📋 Citas de hoy:\n\n"
        for i, c in enumerate(citas):
            texto += f"[{i}] {c.get('time', '')} — {c.get('type', '')}\n"
            if c.get('notes'):
                texto += f"  💬 {c['notes']}\n"
        texto += "\nUsa /borrar_cita <índice> para eliminar"
        await update.message.reply_text(texto)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_cita(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "📝 Uso: /cita HH:MM tipo [notas]\n"
            f"Tipos válidos: {TIPOS_TEXTO}\n\n"
            "Ej: /cita 10:30 médica revisión anual"
        )
        return
    hora = args[0]
    tipo = args[1].lower()
    notas = " ".join(args[2:]) if len(args) > 2 else ""
    if tipo not in TIPOS_VALIDOS:
        await update.message.reply_text(
            f"❌ Tipo '{tipo}' no válido.\nTipos permitidos: {TIPOS_TEXTO}"
        )
        return
    try:
        await create_appointment(hora, tipo, notas)
        msg = f"✅ Cita creada:\n⏰ {hora} — {tipo}"
        if notas:
            msg += f"\n💬 {notas}"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_borrar_cita(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args:
        await update.message.reply_text(
            "🗑 Uso: /borrar_cita <índice>\n"
            "Usa /citas para ver los índices\n"
            "Ej: /borrar_cita 0"
        )
        return
    try:
        index = int(args[0])
        await delete_appointment(index)
        await update.message.reply_text(f"✅ Cita [{index}] eliminada.")
    except ValueError:
        await update.message.reply_text("❌ El índice debe ser un número. Ej: /borrar_cita 0")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_habitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        habitos = await get_habits()
        if not habitos:
            await update.message.reply_text("📭 No hay hábitos registrados hoy.")
            return
        texto = "💪 Hábitos de hoy:\n\n"
        for h in habitos:
            texto += f"• {h.get('habit', '')} = {h.get('value', '')}\n"
        await update.message.reply_text(texto)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_habito(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "Uso: /habito nombre valor\nEj: /habito agua 2"
        )
        return
    try:
        await log_habit(args[0], args[1])
        await update.message.reply_text(f"✅ Hábito registrado: {args[0]} = {args[1]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await cmd_hoy(update, context)
