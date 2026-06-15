"""Tests multiusuario: extracción de user_id y propagación en queries."""

from __future__ import annotations
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from src.bot.api_client import ApiClient, get_user_id


class TestGetUserId:
    def test_get_user_id_from_update(self):
        update = MagicMock()
        update.effective_user.id = 42
        assert get_user_id(update) == 42

    def test_get_user_id_fallback(self):
        update = MagicMock()
        update.effective_user = None
        assert get_user_id(update) == 0


class TestApiClientMultiuser:
    @pytest.mark.asyncio
    async def test_appointments_query_includes_user_id(self):
        captured = {}
        async def fake_get(url, **kwargs):
            captured["url"] = url
            captured["params"] = kwargs.get("params", {})
            return MagicMock(raise_for_status=MagicMock(), json=MagicMock(return_value=[]))
        with patch("src.bot.api_client.httpx.AsyncClient") as cls:
            mc = AsyncMock()
            mc.__aenter__ = AsyncMock(return_value=mc)
            mc.__aexit__ = AsyncMock(return_value=False)
            mc.get = AsyncMock(side_effect=fake_get)
            cls.return_value = mc
            await ApiClient().get_appointments(fecha="2026-06-15", user_id=99)
        assert captured["params"].get("user_id") == 99
        assert "appointments" in captured["url"]

    @pytest.mark.asyncio
    async def test_habits_query_includes_user_id(self):
        captured = {}
        async def fake_get(url, **kwargs):
            captured["params"] = kwargs.get("params", {})
            return MagicMock(raise_for_status=MagicMock(), json=MagicMock(return_value=[]))
        with patch("src.bot.api_client.httpx.AsyncClient") as cls:
            mc = AsyncMock()
            mc.__aenter__ = AsyncMock(return_value=mc)
            mc.__aexit__ = AsyncMock(return_value=False)
            mc.get = AsyncMock(side_effect=fake_get)
            cls.return_value = mc
            await ApiClient().get_habits(fecha="2026-06-15", user_id=77)
        assert captured["params"].get("user_id") == 77
