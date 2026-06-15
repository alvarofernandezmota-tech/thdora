# tests/test_bot/test_nlp_handler.py
import pytest
from unittest.mock import AsyncMock, patch
from src.bot.handlers.nlp import nlp_handler

TEST_USER_ID = 123456789

@pytest.mark.asyncio
async def test_nlp_handler_extracts_user_id(telegram_update, telegram_context):
    update = telegram_update(user_id=TEST_USER_ID, text="nueva cita")
    with patch("src.bot.handlers.nlp.api") as mock_api:
        mock_api.check_appointment_conflict = AsyncMock(return_value=None)
        mock_api.create_appointment = AsyncMock()
        mock_api.get_appointments = AsyncMock(return_value=[])
        mock_api.log_habit = AsyncMock()
        await nlp_handler(update, telegram_context)
    assert update.effective_user.id == TEST_USER_ID

@pytest.mark.asyncio
async def test_nlp_handler_empty_text(telegram_update, telegram_context):
    update = telegram_update(text="")
    with patch("src.bot.handlers.nlp.api") as mock_api:
        await nlp_handler(update, telegram_context)
    assert not update.message.reply_text.called

@pytest.mark.asyncio
async def test_nlp_handler_nueva_cita(telegram_update, telegram_context):
    update = telegram_update(text="nueva cita dentista 10:00")
    with patch("src.bot.handlers.nlp.api") as mock_api:
        mock_api.check_appointment_conflict = AsyncMock(return_value=None)
        mock_api.create_appointment = AsyncMock()
        mock_api.get_appointments = AsyncMock(return_value=[])
        await nlp_handler(update, telegram_context)
        mock_api.create_appointment.assert_called_once()
        call_kwargs = mock_api.create_appointment.call_args[1]
        assert call_kwargs["user_id"] == TEST_USER_ID

@pytest.mark.asyncio
async def test_nlp_handler_log_habito(telegram_update, telegram_context):
    update = telegram_update(text="dormí 8 horas")
    with patch("src.bot.handlers.nlp.api") as mock_api:
        mock_api.log_habit = AsyncMock()
        mock_api.get_appointments = AsyncMock(return_value=[])
        await nlp_handler(update, telegram_context)
        mock_api.log_habit.assert_called_once()
        call_kwargs = mock_api.log_habit.call_args[1]
        assert call_kwargs["user_id"] == TEST_USER_ID

@pytest.mark.asyncio
async def test_nlp_handler_unknown_intent(telegram_update, telegram_context):
    update = telegram_update(text="texto random xyz")
    with patch("src.bot.handlers.nlp.api") as mock_api:
        mock_api.get_appointments = AsyncMock(return_value=[])
        await nlp_handler(update, telegram_context)
    assert update.message.reply_text.called
    reply_text = update.message.reply_text.call_args[0][0]
    assert "/help" in reply_text or "No he entendido" in reply_text
