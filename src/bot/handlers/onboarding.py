import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

logger = logging.getLogger(__name__)

ASK_NAME, ASK_GOAL = range(2)

GOAL_OPTIONS = [["a) Citas y agenda", "b) Habitos saludables"],
                ["c) Bienestar emocional", "d) Todo"]]

GOAL_MAP = {
    "a": "citas y agenda",
    "b": "habitos saludables",
    "c": "bienestar emocional",
    "d": "todo",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "👋 Hola, soy *THDORA*, tu agente de bienestar personal.\n\n"
        "Estoy aqui para ayudarte con tu agenda, tus habitos y tu estado emocional.\n\n"
        "Para empezar, como te llamas?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_NAME


async def received_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if not name or len(name) > 50:
        await update.message.reply_text("Escribeme tu nombre, sin prisa. 😊")
        return ASK_NAME

    context.user_data["name"] = name

    keyboard = ReplyKeyboardMarkup(GOAL_OPTIONS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        f"Encantada, *{name}* 🙂\n\n"
        "En que quieres que te ayude principalmente?\n\n"
        "a) 📅 Citas y agenda\n"
        "b) ✅ Habitos saludables\n"
        "c) 🧠 Bienestar emocional\n"
        "d) 🌟 Todo",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    return ASK_GOAL


async def received_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().lower()
    key = text[0] if text else ""

    if key not in GOAL_MAP:
        await update.message.reply_text(
            "Elige una opcion: a, b, c o d.",
            reply_markup=ReplyKeyboardMarkup(GOAL_OPTIONS, one_time_keyboard=True, resize_keyboard=True),
        )
        return ASK_GOAL

    goal = GOAL_MAP[key]
    context.user_data["goal"] = goal
    name = context.user_data.get("name", "")

    await update.message.reply_text(
        f"✅ Perfecto, *{name}*.\n\n"
        f"Me enfocaere en ayudarte con *{goal}*.\n\n"
        "Aqui tienes los comandos principales:\n"
        "📅 /citas — gestiona tus citas\n"
        "✅ /habitos — registra tus habitos\n"
        "💬 Escribeme cualquier cosa — entiendo lenguaje natural\n\n"
        "Empezamos cuando quieras! 🚀",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )

    # TODO futuro: guardar en BD user_profile (user_id, name, goal, created_at)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "De acuerdo, puedes volver cuando quieras con /start. 👋",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def get_onboarding_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("onboarding", start),
        ],
        states={
            ASK_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_name)
            ],
            ASK_GOAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_goal)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="onboarding",
        persistent=False,
    )
