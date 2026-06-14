"""
Cliente Groq para THDORA — v2.

Cambios respecto a v1:
  - Timeout read subido a 90s
  - Retry automático con exponential backoff (tenacity, máx 3 intentos)
  - En timeout definitivo devuelve mensaje amigable, no propaga excepción
  - build_system_prompt() inyecta fecha real en cada llamada
  - chat() acepta context_block opcional para datos dinámicos del usuario
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

logger = logging.getLogger(__name__)

_GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
_TIMEOUT = httpx.Timeout(connect=10.0, read=90.0, write=10.0, pool=5.0)

_MSG_TIMEOUT = (
    "Lo siento, tardo un poco más de lo normal. "
    "Inténtalo en unos segundos 🙏"
)


def build_system_prompt(user_name: str = "Usuario") -> str:
    """Genera el system prompt con fecha actual inyectada dinámicamente."""
    now = datetime.now()
    fecha = now.strftime("%A %d de %B de %Y, %H:%M")

    return f"""Eres THDORA, el asistente personal de {user_name}, especializado en gestión \
de agenda y hábitos diarios.

📅 Hoy es {fecha}.

ROL Y CAPACIDADES:
- Ayudas a gestionar citas, eventos y hábitos personales.
- Tienes acceso a tools para consultar, crear y gestionar citas y hábitos.
- Cuando el usuario quiera actuar sobre sus datos, usas las herramientas disponibles.

LÍMITES CLAROS:
- No inventas datos: si no tienes información, lo dices con honestidad.
- No accedes a internet ni a información externa.
- No respondes sobre temas ajenos a agenda, hábitos y bienestar personal.
- Si el usuario pregunta algo fuera de tu ámbito, lo rediriges amablemente.

FORMATO DE RESPUESTA:
- Conciso: máximo 3 párrafos cortos por respuesta.
- Usa emojis con moderación (1-2 por respuesta como máximo).
- Responde siempre en el mismo idioma que el usuario.
- Sé directo: no repitas lo que el usuario ya sabe."""


class GroqError(Exception):
    """Error en la llamada a la API de Groq."""
    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code


class GroqClient:
    """
    Cliente HTTP asíncrono para la API de Groq (compatible OpenAI).

    Incluye retry automático con backoff exponencial ante timeouts y
    errores de red transitorios. En timeout definitivo devuelve mensaje
    amigable en lugar de propagar la excepción.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_name: str = "Usuario",
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        if not self.api_key:
            raise GroqError("GROQ_API_KEY no está configurada. Añádela al .env")
        self.model = model or _DEFAULT_MODEL
        self.user_name = user_name
        self._system_override: Optional[str] = system_prompt

    def _get_system(self) -> str:
        return self._system_override or build_system_prompt(self.user_name)

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=False,
    )
    async def _call_api(self, payload: Dict[str, Any]) -> str:
        """Llamada real a Groq con retry. Lanza GroqError en error HTTP."""
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

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.4,
        max_tokens: int = 512,
        context_block: str = "",
    ) -> str:
        """
        Envía mensajes a Groq y devuelve el texto de la respuesta.

        Args:
            messages:      Lista de {role, content}. El system se añade automáticamente.
            temperature:   Creatividad (0 determinista, 1 creativo).
            max_tokens:    Máx tokens en la respuesta.
            context_block: Bloque de texto con datos dinámicos del usuario
                           (citas/hábitos de hoy). Se inyecta al final del system prompt.

        Returns:
            Texto de la respuesta. En timeout definitivo devuelve mensaje amigable.
        """
        system = self._get_system()
        if context_block:
            system = f"{system}\n\n{context_block}"

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}] + messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            return await self._call_api(payload)
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            logger.error("Timeout definitivo con Groq tras 3 intentos: %s", exc)
            return _MSG_TIMEOUT
        except GroqError:
            raise

    async def ask(self, user_message: str, **kwargs) -> str:
        """Atajo: envía un mensaje de usuario y devuelve la respuesta."""
        return await self.chat([{"role": "user", "content": user_message}], **kwargs)


# Instancia global
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
