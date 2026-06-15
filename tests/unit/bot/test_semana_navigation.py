"""Tests para navegación semanal."""

from __future__ import annotations
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from src.bot.handlers.semana_nav import _week_center_label, get_week_range


class TestGetWeekRange:
    def test_get_week_range_offset_0(self):
        monday, sunday = get_week_range(0)
        today = date.today()
        expected_monday = today - timedelta(days=today.weekday())
        assert monday == expected_monday
        assert sunday == expected_monday + timedelta(days=6)
        assert monday.weekday() == 0
        assert sunday.weekday() == 6

    def test_get_week_range_offset_minus1(self):
        monday_current, _ = get_week_range(0)
        monday_prev, sunday_prev = get_week_range(-1)
        assert monday_prev == monday_current - timedelta(weeks=1)
        assert sunday_prev == monday_prev + timedelta(days=6)

    def test_get_week_range_offset_plus2(self):
        monday_current, _ = get_week_range(0)
        monday_future, sunday_future = get_week_range(2)
        assert monday_future == monday_current + timedelta(weeks=2)
        assert sunday_future == monday_future + timedelta(days=6)


class TestWeekLabel:
    def test_week_center_button_label(self):
        label = _week_center_label(date(2026, 6, 15), date(2026, 6, 21))
        assert "15" in label and "21" in label and "jun" in label and "–" in label


class TestWeekView:
    @pytest.mark.asyncio
    async def test_empty_week_shows_message(self):
        from src.bot.handlers.semana_nav import show_week_view
        update = MagicMock()
        update.callback_query = None
        update.effective_user.id = 123
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.user_data = {}
        with patch("src.bot.handlers.semana_nav.ApiClient") as mock_api_cls:
            mock_api = AsyncMock()
            mock_api.get_appointments_range = AsyncMock(return_value=[])
            mock_api_cls.return_value = mock_api
            await show_week_view(update, context)
        text = update.message.reply_text.call_args[0][0]
        assert "libre" in text.lower() or "📭" in text

    @pytest.mark.asyncio
    async def test_navigation_offset_increments(self):
        from src.bot.handlers.semana_nav import show_week_view
        query = MagicMock()
        query.data = "WEEK_NEXT"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        update = MagicMock()
        update.callback_query = query
        update.effective_user.id = 123
        context = MagicMock()
        context.user_data = {"week_offset": 0}
        with patch("src.bot.handlers.semana_nav.ApiClient") as mock_api_cls:
            mock_api = AsyncMock()
            mock_api.get_appointments_range = AsyncMock(return_value=[])
            mock_api_cls.return_value = mock_api
            await show_week_view(update, context)
        assert context.user_data["week_offset"] == 1
