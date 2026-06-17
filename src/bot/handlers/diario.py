"""Handler /diario — guarda una entrada en el diario del día en yggdrasil-dew."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.middleware import require_allowed_user
from src.services.github_client import get_github_client

logger = logging.getLogger(__name__)


@require_allowed_user
async def diario_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Guarda el texto del mensaje como entrada en el diario de hoy en yggdrasil-dew."""
    user_id = update.effective_user.id
    text = " ".join(context.args).strip() if context.args else ""

    if not text:
        await update.message.reply_text(
            "\u270f\ufe0f Escribe el texto que quieres guardar en el diario de hoy.\n"
            "Ejemplo: `/diario Hoy empecé a leer Dune`",
            parse_mode="Markdown",
        )
        return

    ok = await get_github_client().append_to_diario(text, user_id)

    if ok:
        await update.message.reply_text("\u2705 Entrada guardada en el diario de hoy.")
    else:
        logger.error("diario_handler: fallo | user_id=%s | chars=%d", user_id, len(text))
        await update.message.reply_text(
            "\u274c No se pudo guardar la entrada. Inténtalo de nuevo."
        )
