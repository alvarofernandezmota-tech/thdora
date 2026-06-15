# tests/test_api/test_summary.py
import pytest

TEST_USER_ID = 123456789
TEST_DATE = "2026-06-15"

@pytest.mark.asyncio
async def test_get_summary_ok(app_client):
    response = await app_client.get(f"/summary/{TEST_DATE}?user_id={TEST_USER_ID}")
    assert response.status_code == 200
    data = response.json()
    assert "date" in data
    assert "appointments" in data
    assert "habits" in data

@pytest.mark.asyncio
async def test_get_week_summary_ok(app_client):
    response = await app_client.get(f"/summary/week/{TEST_DATE}?user_id={TEST_USER_ID}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert TEST_DATE in data

@pytest.mark.asyncio
async def test_summary_missing_user_id(app_client):
    response = await app_client.get(f"/summary/{TEST_DATE}")
    assert response.status_code == 422
