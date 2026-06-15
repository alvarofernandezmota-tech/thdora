# src/bot/api_client.py
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

_API_BASE = os.getenv("THDORA_API_URL", "http://localhost:8000")
_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code


def _raise_for_status(r: httpx.Response) -> None:
    if r.is_error:
        detail = ""
        try:
            detail = r.json().get("detail", "")
        except Exception:
            detail = r.text[:200]
        raise ApiError(f"HTTP {r.status_code}: {detail}", status_code=r.status_code)


def _validate_user_id(user_id: int) -> None:
    if not user_id or user_id <= 0:
        raise ValueError("user_id es obligatorio y debe ser > 0")


class ThdoraApiClient:
    def __init__(self, base_url: str = _API_BASE) -> None:
        self.base_url = base_url.rstrip("/")

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                r = await client.get(f"{self.base_url}/")
                return r.status_code == 200
        except httpx.RequestError:
            return False

    async def get_appointments(self, date_str: str, user_id: int) -> List[Dict[str, Any]]:
        _validate_user_id(user_id)
        return await self._get(f"/appointments/{date_str}?user_id={user_id}")

    async def get_appointments_week(self, date_str: str, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        _validate_user_id(user_id)
        return await self._get(f"/appointments/week/{date_str}?user_id={user_id}")

    async def create_appointment(self, date_str: str, time: str, name: str, apt_type: str, notes: str = "", *, user_id: int) -> Dict[str, Any]:
        _validate_user_id(user_id)
        return await self._post(f"/appointments/{date_str}?user_id={user_id}", json={"time": time, "name": name, "type": apt_type, "notes": notes})

    async def delete_appointment(self, date_str: str, index: int, user_id: int) -> bool:
        _validate_user_id(user_id)
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.delete(f"{self.base_url}/appointments/{date_str}/{index}?user_id={user_id}")
                if r.status_code == 404:
                    return False
                _raise_for_status(r)
                return True
        except httpx.RequestError as exc:
            raise ApiError(f"Error DELETE appointment: {exc}") from exc

    async def update_appointment(self, date_str: str, index: int, time: Optional[str] = None, name: Optional[str] = None, apt_type: Optional[str] = None, notes: Optional[str] = None, *, user_id: int) -> Dict[str, Any]:
        _validate_user_id(user_id)
        payload: Dict[str, Any] = {}
        if time is not None: payload["time"] = time
        if name is not None: payload["name"] = name
        if apt_type is not None: payload["type"] = apt_type
        if notes is not None: payload["notes"] = notes
        return await self._put(f"/appointments/{date_str}/{index}?user_id={user_id}", json=payload)

    async def check_appointment_conflict(self, date_str: str, time: str, user_id: int) -> Optional[Dict[str, Any]]:
        _validate_user_id(user_id)
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.get(f"{self.base_url}/appointments/{date_str}/conflict/{time.replace(':', '%3A')}?user_id={user_id}")
                if r.status_code in (404, 204):
                    return None
                if r.status_code == 200:
                    return r.json()
                return None
        except Exception:
            return None

    async def get_habits(self, date_str: str, user_id: int) -> Dict[str, str]:
        _validate_user_id(user_id)
        raw: List[Dict[str, str]] = await self._get(f"/habits/{date_str}?user_id={user_id}")
        return {item["habit"]: item["value"] for item in raw}

    async def log_habit(self, date_str: str, habit: str, value: str, user_id: int) -> bool:
        _validate_user_id(user_id)
        await self._post(f"/habits/{date_str}?user_id={user_id}", json={"habit": habit, "value": value})
        return True

    async def delete_habit(self, date_str: str, habit: str, user_id: int) -> bool:
        _validate_user_id(user_id)
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.delete(f"{self.base_url}/habits/{date_str}/{habit}?user_id={user_id}")
                if r.status_code == 404:
                    return False
                _raise_for_status(r)
                return True
        except httpx.RequestError as exc:
            raise ApiError(f"Error DELETE habit: {exc}") from exc

    async def update_habit(self, date_str: str, habit: str, value: str, user_id: int) -> Dict[str, str]:
        _validate_user_id(user_id)
        return await self._put(f"/habits/{date_str}/{habit}?user_id={user_id}", json={"value": value})

    async def get_summary(self, date_str: str, user_id: int) -> Dict[str, Any]:
        _validate_user_id(user_id)
        return await self._get(f"/summary/{date_str}?user_id={user_id}")

    async def get_week_summary(self, date_str: str, user_id: int) -> Dict[str, Dict[str, Any]]:
        _validate_user_id(user_id)
        return await self._get(f"/summary/week/{date_str}?user_id={user_id}")

    async def _get(self, path: str) -> Any:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.get(f"{self.base_url}{path}")
                _raise_for_status(r)
                return r.json()
        except httpx.RequestError as exc:
            raise ApiError(f"Error GET {path}: {exc}") from exc

    async def _post(self, path: str, json: Dict[str, Any]) -> Any:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.post(f"{self.base_url}{path}", json=json)
                _raise_for_status(r)
                return r.json()
        except httpx.RequestError as exc:
            raise ApiError(f"Error POST {path}: {exc}") from exc

    async def _put(self, path: str, json: Dict[str, Any]) -> Any:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.put(f"{self.base_url}{path}", json=json)
                _raise_for_status(r)
                return r.json()
        except httpx.RequestError as exc:
            raise ApiError(f"Error PUT {path}: {exc}") from exc
