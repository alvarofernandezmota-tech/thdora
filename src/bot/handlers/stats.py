import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from src.agents.metrics import MetricsCollector

logger = logging.getLogger(__name__)
_metrics = MetricsCollector()


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await update.message.chat.send_action("typing")

    stats = await _metrics.get_stats(user_id)
    if not stats:
        await update.message.reply_text("No tengo datos suficientes aun. Sigue usando THDORA! 😊")
        return

    mood_str = f"{stats['mood_average']:.1f}/10" if stats.get("mood_average") is not None else "sin datos"

    text = (
        "📊 *Tu semana en THDORA:*\n\n"
        f"💬 {stats['nlp_messages']} mensajes a THDORA\n"
        f"📅 {stats['appointments_created']} citas creadas\n"
        f"✅ {stats['habits_logged']} habitos registrados\n"
        f"🧠 Estado emocional promedio: {mood_str}\n"
        f"⚡ THDORA entendio el {stats['nlp_success_rate']}% de tus mensajes"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


def register(app) -> None:
    app.add_handler(CommandHandler("stats", stats_handler))
