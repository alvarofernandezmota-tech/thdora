"""
Tests unitarios de ThdoraApiClient.
Verifica que cada método llama al endpoint correcto con los parámetros correctos.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.conftest import TEST_DATE, TEST_USER_ID, TEST_HABIT, TEST_APT_NAME, TEST_APT_TIME


# Helper: crea un httpx.Response fake
def _fake_resp(json_data, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json        = MagicMock(return_value=json_data)
    resp.is_error    = status_code >= 400
    return resp


@pytest.fixture
def api_client():
    """Instancia de ThdoraApiClient con _client mockeado."""
    from src.bot.api_client import ThdoraApiClient
    client = ThdoraApiClient()
    ThdoraApiClient._client = AsyncMock()
    ThdoraApiClient._client.request = AsyncMock()
    return client


# ── Habits ────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_habits_calls_correct_endpoint(api_client):
    expected = {TEST_HABIT: "2L"}
    api_client._client.request = AsyncMock(return_value=_fake_resp(expected))
    result = await api_client.get_habits(TEST_DATE, TEST_USER_ID)
    api_client._client.request.assert_called_once()
    call_args = api_client._client.request.call_args
    assert "GET" in call_args[0]
    assert f"/habits/{TEST_DATE}" in call_args[0][1]
    assert result == expected


@pytest.mark.asyncio
async def test_log_habit_sends_correct_body(api_client):
    expected = {"habit": TEST_HABIT, "value": "2L"}
    api_client._client.request = AsyncMock(return_value=_fake_resp(expected))
    await api_client.log_habit(TEST_DATE, TEST_HABIT, "2L", TEST_USER_ID)
    call_kwargs = api_client._client.request.call_args[1]
    assert call_kwargs["json"] == {"habit": TEST_HABIT, "value": "2L"}


@pytest.mark.asyncio
async def test_delete_habit_returns_true_on_204(api_client):
    api_client._client.request = AsyncMock(return_value=_fake_resp({}, status_code=204))
    result = await api_client.delete_habit(TEST_DATE, TEST_HABIT, TEST_USER_ID)
    assert result is True


@pytest.mark.asyncio
async def test_update_habit_sends_value(api_client):
    expected = {"habit": TEST_HABIT, "value": "3L"}
    api_client._client.request = AsyncMock(return_value=_fake_resp(expected))
    result = await api_client.update_habit(TEST_DATE, TEST_HABIT, "3L", TEST_USER_ID)
    call_kwargs = api_client._client.request.call_args[1]
    assert call_kwargs["json"] == {"value": "3L"}
    assert result == expected


# ── Appointments ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_appointments_calls_correct_endpoint(api_client):
    payload = [{"name": TEST_APT_NAME, "time": TEST_APT_TIME}]
    api_client._client.request = AsyncMock(return_value=_fake_resp(payload))
    result = await api_client.get_appointments(TEST_DATE, TEST_USER_ID)
    call_args = api_client._client.request.call_args[0]
    assert f"/appointments/{TEST_DATE}" in call_args[1]
    assert result == payload


@pytest.mark.asyncio
async def test_create_appointment_sends_data_dict(api_client):
    data = {"name": TEST_APT_NAME, "time": TEST_APT_TIME, "type": "trabajo"}
    api_client._client.request = AsyncMock(return_value=_fake_resp(data))
    await api_client.create_appointment(TEST_DATE, data, TEST_USER_ID)
    call_kwargs = api_client._client.request.call_args[1]
    assert call_kwargs["json"] == data


@pytest.mark.asyncio
async def test_delete_appointment_returns_true_on_204(api_client):
    api_client._client.request = AsyncMock(return_value=_fake_resp({}, status_code=204))
    result = await api_client.delete_appointment(TEST_DATE, 0, TEST_USER_ID)
    assert result is True


# ── Habit Config ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_upsert_habit_config_sends_data_dict(api_client):
    data = {"name": TEST_HABIT, "habit_type": "numeric", "unit": "L", "quick_vals": ["1L", "2L"]}
    api_client._client.request = AsyncMock(return_value=_fake_resp(data))
    result = await api_client.upsert_habit_config(data, TEST_USER_ID)
    call_kwargs = api_client._client.request.call_args[1]
    assert call_kwargs["json"] == data


@pytest.mark.asyncio
async def test_get_habit_config_returns_none_on_404(api_client):
    from src.bot.api_client import ApiError
    resp_404 = _fake_resp({"detail": "Not found"}, status_code=404)
    resp_404.is_error = True
    api_client._client.request = AsyncMock(return_value=resp_404)
    result = await api_client.get_habit_config(TEST_HABIT, TEST_USER_ID)
    assert result is None


# ── User Config ───────────────────────────────────────────────
@pytest.mark.asyncio
async def test_update_user_config_sends_data_dict(api_client):
    data   = {"daily_summary_enabled": False}
    result_data = {"daily_summary_enabled": False}
    api_client._client.request = AsyncMock(return_value=_fake_resp(result_data))
    result = await api_client.update_user_config(TEST_USER_ID, data)
    call_kwargs = api_client._client.request.call_args[1]
    assert call_kwargs["json"] == data


@pytest.mark.asyncio
async def test_validate_user_id_raises_on_zero(api_client):
    from src.bot.api_client import ApiError
    with pytest.raises(ValueError, match="user_id"):
        await api_client.get_habits(TEST_DATE, 0)
