"""
Tests del handler de configuración.
Verifica: menú, toggle notificaciones, upsert hab config, delete hab config.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import (
    TEST_USER_ID, TEST_HABIT,
    make_update_callback, make_update_message, make_context,
)


@pytest.mark.asyncio
async def test_save_habit_config_llama_upsert(mock_api):
    """_save_habit_config llama a upsert_habit_config(data:dict, user_id)."""
    with patch("src.bot.handlers.config.api", mock_api):
        from src.bot.handlers.config import _save_habit_config
        msg = AsyncMock()
        msg.reply_text = AsyncMock()
        ctx = make_context({
            "cfg_nombre":   TEST_HABIT,
            "cfg_type":     "numeric",
            "cfg_user_id":  TEST_USER_ID,
        })
        await _save_habit_config(msg, ctx, "L", ["1L", "2L"])
        mock_api.upsert_habit_config.assert_awaited_once()
        call_args = mock_api.upsert_habit_config.call_args
        # Primer arg debe ser dict, segundo user_id
        assert isinstance(call_args[0][0], dict)
        assert call_args[0][1] == TEST_USER_ID


@pytest.mark.asyncio
async def test_delete_hab_config_llama_api(mock_api):
    """cfg_del_hab_confirm llama a delete_habit_config(nombre, user_id)."""
    with patch("src.bot.handlers.config.api", mock_api):
        from src.bot.handlers.config import cfg_del_hab_confirm, CFG_MENU
        update = make_update_callback("cfgdelok")
        ctx    = make_context({"cfg_del_nombre": TEST_HABIT})
        result = await cfg_del_hab_confirm(update, ctx)
        mock_api.delete_habit_config.assert_awaited_once_with(TEST_HABIT, TEST_USER_ID)
        assert result == CFG_MENU


@pytest.mark.asyncio
async def test_toggle_summary_llama_update_user_config(mock_api):
    """notif_menu_action toggle llama a update_user_config con dict."""
    with patch("src.bot.handlers.config.api", mock_api):
        from src.bot.handlers.config import notif_menu_action, NOTIF_MENU
        update = make_update_callback("notif_toggle_summary")
        ctx    = make_context({
            "notif_user_id": TEST_USER_ID,
            "notif_cfg": {"daily_summary_enabled": True},
        })
        result = await notif_menu_action(update, ctx)
        mock_api.update_user_config.assert_awaited_once_with(
            TEST_USER_ID, {"daily_summary_enabled": False}
        )
        assert result == NOTIF_MENU


@pytest.mark.asyncio
async def test_get_habit_configs_usa_user_id(mock_api):
    """_show_hab_configs llama a get_habit_configs(user_id), no get_all_habit_configs."""
    mock_api.get_habit_configs = AsyncMock(return_value=[])
    with patch("src.bot.handlers.config.api", mock_api):
        from src.bot.handlers.config import _show_hab_configs
        query = make_update_callback("cfg_habitos").callback_query
        query.edit_message_text = AsyncMock()
        await _show_hab_configs(query, TEST_USER_ID)
        mock_api.get_habit_configs.assert_awaited_once_with(TEST_USER_ID)


@pytest.mark.asyncio
async def test_cfg_recv_nombre_guarda_nombre(mock_api):
    """cfg_recv_nombre guarda nombre en user_data y avanza."""
    mock_api.get_habit_configs = AsyncMock(return_value=[])
    with patch("src.bot.handlers.config.api", mock_api):
        from src.bot.handlers.config import cfg_recv_nombre, CFG_TYPE
        update = make_update_message(text=TEST_HABIT)
        ctx    = make_context({"cfg_user_id": TEST_USER_ID})
        result = await cfg_recv_nombre(update, ctx)
        assert ctx.user_data["cfg_nombre"] == TEST_HABIT
        assert result == CFG_TYPE
