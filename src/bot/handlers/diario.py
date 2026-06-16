import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.services.github_client import GitHubClient

logger = logging.getLogger(__name__)


async def diario_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    text = " ".join(context.args).strip() if context.args else ""

    if not text:
        await update.message.reply_text(
            "✏️ Escribe el texto que quieres guardar en el diario de hoy."
        )
        return

    ok = await GitHubClient().append_to_diario(text, user_id)

    if ok:
        await update.message.reply_text("✅ Entrada guardada en el diario de hoy.")
    else:
        logger.error("diario_handler: fallo al guardar | user_id=%s | chars=%d", user_id, len(text))
        await update.message.reply_text("❌ No se pudo guardar la entrada. Inténtalo de nuevo.")
