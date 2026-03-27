# src/bot/api_client.py
import httpx

BASE_URL = "http://localhost:8000"

async def get_summary() -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/summary/hoy")
        r.raise_for_status()
        return r.json()

async def get_appointments() -> list:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/appointments")
        r.raise_for_status()
        return r.json()

async def create_appointment(data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/appointments", json=data)
        r.raise_for_status()
        return r.json()

async def log_habit(data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/habits", json=data)
        r.raise_for_status()
        return r.json()