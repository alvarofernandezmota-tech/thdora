"""Handler NLP — LangGraph (thread_id=user_id) con fallback a GroqRouter — v0.20.1."""
from __future__ import annotations
import logging
import traceback
import httpx
from langchain_core.messages import HumanMessage
from telegram import Update
from telegram.constants import ChatAction
from telegram.error import NetworkError, TimedOut
from telegram.ext import ContextTypes
from src.bot.middleware import require_allowed_user

logger = logging.getLogger(__name__)

_TRIVIALES = {"hola", "ok", "vale", "gracias", "de nada", "👍", "👌", "si", "sí", "no", "buenas", "hey"}


def _get_graph():
    try:
        from src.bot.agents.thdora_agent import build_thdora_graph
        return build_thdora_graph()
    except ImportError:
        return None


@require_allowed_user
async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    user_text = update.message.text
    user_id = update.effective_user.id if update.effective_user else 0
    chat_id = update.effective_chat.id if update.effective_chat else 0
    nombre_usuario = (
        context.user_data.get("name")
        or (update.effective_user.first_name if update.effective_user else None)
    )

    text_lower = user_text.strip().lower()
    if text_lower in _TRIVIALES or len(text_lower) < 3:
        await update.message.reply_text("👋 ¿En qué puedo ayudarte?")
        return

    await update.effective_chat.send_action(ChatAction.TYPING)
    provisional = await update.message.reply_text("⏳ Procesando...")

    graph = _get_graph()

    try:
        if graph is not None:
            # —— LangGraph con memoria persistente por usuario ——
            config = {"configurable": {"thread_id": str(user_id)}}
            inputs = {
                "messages": [HumanMessage(content=user_text)],
                "user_id": user_id,
                "nombre_usuario": nombre_usuario,
                "context_summary": context.user_data.get("context_summary", ""),
                "long_term_memory": "",
                "pending_action": None,
                "last_appointments": context.user_data.get("last_appointments", []),
                "last_habits": context.user_data.get("last_habits", []),
            }
            result = await graph.ainvoke(inputs, config=config)
            response_text = result["messages"][-1].content
        else:
            # —— Fallback GroqRouter ——
            from src.bot.llm_factory import get_router
            from src.bot.groq_router import AmbiguityRequest, ToolCallResult
            nlp_history = context.user_data.setdefault("nlp_history", [])
            router = get_router()
            result = await router.process(
                user_text=user_text, user_id=user_id,
                history=nlp_history, nombre_usuario=nombre_usuario,
            )
            if isinstance(result, AmbiguityRequest):
                response_text = result.question_to_user
            elif hasattr(result, "message_to_user"):
                response_text = result.message_to_user
            else:
                response_text = str(result)
            nlp_history = context.user_data.setdefault("nlp_history", [])
            nlp_history.append({"role": "user", "content": user_text})
            nlp_history.append({"role": "assistant", "content": response_text})
            if len(nlp_history) > 20:
                nlp_history[:] = nlp_history[-20:]

        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id, text=response_text
        )

    except httpx.TimeoutException:
        logger.error("Timeout NLP user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(chat_id=chat_id, message_id=provisional.message_id,
            text="⏳ El servicio tardó demasiado. Inténtalo de nuevo.")
    except httpx.ConnectError:
        logger.error("ConnectError NLP user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(chat_id=chat_id, message_id=provisional.message_id,
            text="🔌 No se pudo conectar con el servicio de IA.")
    except TimedOut:
        logger.error("TimedOut NLP user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(chat_id=chat_id, message_id=provisional.message_id,
            text="⏳ Telegram agotó el tiempo. Inténtalo de nuevo.")
    except NetworkError:
        logger.error("NetworkError NLP user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(chat_id=chat_id, message_id=provisional.message_id,
            text="🔌 Error de red. Comprueba tu conexión.")
    except Exception:
        logger.error("Error inesperado NLP user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(chat_id=chat_id, message_id=provisional.message_id,
            text="❌ Ocurrió un error inesperado.")
