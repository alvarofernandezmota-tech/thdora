"""
Tests para src/bot/handlers/menu.py

Cubre:
 - cmd_start: llama reply_text con saludo + teclado
 - cb_menu_home: llama reply_text desde callback
 - cb_quick_dispatch: rutas quick_nueva / quick_habito / quick_config
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.handlers.menu import cmd_start, cb_menu_home, cb_quick_dispatch


def _make_message_update():
    update  = MagicMock()
    message = AsyncMock()
    message.reply_text = AsyncMock()
    update.message = message
    return update


def _make_callback(data):
    update = MagicMock()
    query  = AsyncMock()
    query.data = data
    query.answer = AsyncMock()
    query.message = AsyncMock()
    query.message.reply_text = AsyncMock()
    update.callback_query = query
    update.message = None
    return update


def _make_context(user_data=None):
    ctx = MagicMock()
    ctx.user_data = user_data or {}
    return ctx


pytestmark = pytest.mark.asyncio


class TestCmdStart:
    @patch("src.bot.handlers.menu.api")
    async def test_llama_reply_text(self, mock_api):
        mock_api.get_appointments = AsyncMock(return_value=[])
        update  = _make_message_update()
        context = _make_context()
        await cmd_start(update, context)
        update.message.reply_text.assert_awaited_once()

    @patch("src.bot.handlers.menu.api")
    async def test_muestra_citas_si_hay(self, mock_api):
        mock_api.get_appointments = AsyncMock(return_value=[{"time": "10:00", "name": "X", "type": "personal"}])
        update  = _make_message_update()
        context = _make_context()
        await cmd_start(update, context)
        call_kwargs = update.message.reply_text.call_args
        assert "1 cita" in call_kwargs[0][0]

    @patch("src.bot.handlers.menu.api")
    async def test_no_falla_si_api_error(self, mock_api):
        mock_api.get_appointments = AsyncMock(side_effect=Exception("fallo"))
        update  = _make_message_update()
        context = _make_context()
        await cmd_start(update, context)  # no debe lanzar
        update.message.reply_text.assert_awaited_once()


class TestCbMenuHome:
    @patch("src.bot.handlers.menu.api")
    async def test_llama_reply_text(self, mock_api):
        mock_api.get_appointments = AsyncMock(return_value=[])
        update  = _make_callback("menu_home")
        context = _make_context()
        await cb_menu_home(update, context)
        update.callback_query.message.reply_text.assert_awaited_once()


class TestCbQuickDispatch:
    async def test_quick_nueva_sin_fecha_muestra_franjas(self):
        update  = _make_callback("quick_nueva")
        context = _make_context()
        await cb_quick_dispatch(update, context)
        update.callback_query.message.reply_text.assert_awaited_once()

    async def test_quick_nueva_con_fecha_guarda_en_user_data(self):
        update  = _make_callback("quick_nueva_2026-04-15")
        context = _make_context()
        await cb_quick_dispatch(update, context)
        assert context.user_data.get("nueva_date") == "2026-04-15"

    async def test_quick_habito_sin_fecha_usa_hoy(self):
        update  = _make_callback("quick_habito")
        context = _make_context()
        await cb_quick_dispatch(update, context)
        from datetime import date
        assert context.user_data.get("habito_date") == str(date.today())

    async def test_quick_habito_con_fecha_guarda_fecha(self):
        update  = _make_callback("quick_habito_2026-04-20")
        context = _make_context()
        await cb_quick_dispatch(update, context)
        assert context.user_data.get("habito_date") == "2026-04-20"

    async def test_quick_config_responde(self):
        update  = _make_callback("quick_config")
        context = _make_context()
        await cb_quick_dispatch(update, context)
        update.callback_query.message.reply_text.assert_awaited_once()
