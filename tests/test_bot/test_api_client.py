# tests/test_bot/test_api_client.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.bot.api_client import ThdoraApiClient, _validate_user_id

TEST_USER_ID = 123456789
TEST_DATE = "2026-06-15"

def test_validate_user_id_raises_on_zero():
    with pytest.raises(ValueError, match="user_id es obligatorio"):
        _validate_user_id(0)

def test_validate_user_id_raises_on_negative():
    with pytest.raises(ValueError, match="user_id es obligatorio"):
        _validate_user_id(-1)

@pytest.mark.asyncio
async def test_get_appointments_calls_correct_url():
    client = ThdoraApiClient()
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.is_error = False
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        await client.get_appointments(TEST_DATE, user_id=TEST_USER_ID)
        call_args = mock_client.return_value.__aenter__.return_value.get.call_args[0][0]
        assert f"user_id={TEST_USER_ID}" in call_args

@pytest.mark.asyncio
async def test_health_returns_true_on_200():
    client = ThdoraApiClient()
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        result = await client.health()
        assert result is True
