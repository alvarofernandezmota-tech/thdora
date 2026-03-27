"""
Cliente Groq para THDORA.

Lee GROQ_API_KEY del entorno (.env). Nunca hardcodees la key.

Uso rápido::

    from src.ai.groq_client import ask
    response = await ask("Resumén mis hábitos de hoy")

Modelos disponibles (gratuitos)::

    llama3-8b-8192      → más rápido, contexto 8k   (DEFAULT)
    llama3-70b-8192     → más potente, contexto 8k
    mixtral-8x7b-32768  → buen balance, contexto 32k
    gemma2-9b-it        → alternativa ligera
"""

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

_GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=5.0)

# System prompt base de THDORA
_SYSTEM_PROMPT = """
Eres THDORA, un asistente personal inteligente de gestión de vida.
Ayudas al usuario a gestionar sus citas, hábitos y rutinas diarias.
Respondes siempre en español, de forma concisa y útil.
Si el usuario te pide algo que no puedes hacer (como acceder a internet),
lo indicas con claridad pero sigues siendo útil con lo que tienes.
""".strip()


class GroqError(Exception):
    """Error en la llamada a la API de Groq."""
    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code


class GroqClient:
    """
    Cliente HTTP asíncrono para la API de Groq (compatible OpenAI).

    Args:
        api_key: Groq API key. Por defecto usa GROQ_API_KEY del entorno.
        model:   Modelo a usar. Por defecto GROQ_MODEL o llama3-8b-8192.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        if not self.api_key:
            raise GroqError("GROQ_API_KEY no está configurada. Añádela al .env")
        self.model  = model or _DEFAULT_MODEL
        self.system = system_prompt or _SYSTEM_PROMPT

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.4,
        max_tokens: int = 512,
    ) -> str:
        """
        Envía una lista de mensajes y devuelve el texto de la respuesta.

        Args:
            messages:    Lista de {"role": "user"|"assistant", "content": "..."}.
                         El system prompt se añade automáticamente.
            temperature: Creatividad (0 = determinista, 1 = creativo).
            max_tokens:  Máx tokens en la respuesta.

        Returns:
            Texto de la respuesta del modelo.

        Raises:
            GroqError: Si la API devuelve error.
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "system", "content": self.system}] + messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.post(
                    _GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if r.is_error:
                    detail = ""
                    try:
                        detail = r.json().get("error", {}).get("message", r.text[:200])
                    except Exception:
                        detail = r.text[:200]
                    raise GroqError(f"HTTP {r.status_code}: {detail}", status_code=r.status_code)
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
        except httpx.RequestError as exc:
            raise GroqError(f"Error de red con Groq: {exc}") from exc

    async def ask(self, user_message: str, **kwargs) -> str:
        """Atajo: envía un mensaje de usuario y devuelve la respuesta."""
        return await self.chat([{"role": "user", "content": user_message}], **kwargs)


# Instancia global (lazy — solo se crea si hay GROQ_API_KEY)
_client: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """Devuelve (o crea) la instancia global del cliente Groq."""
    global _client
    if _client is None:
        _client = GroqClient()
    return _client


async def ask(message: str, **kwargs) -> str:
    """Atajo global: pregunta al LLM y devuelve la respuesta en texto."""
    return await get_groq_client().ask(message, **kwargs)
