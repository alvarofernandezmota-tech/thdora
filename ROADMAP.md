# 🗺️ THDORA — ROADMAP

Navegación rápida: [README](README.md) · [CHANGELOG](CHANGELOG.md)

El roadmap detallado de versiones futuras (v0.18+) vive en [yggdrasil-dew/proyectos/thdora.md](https://github.com/alvarofernandezmota-tech/yggdrasil-dew/blob/main/proyectos/thdora.md). Este archivo solo refleja el estado real del branch main.

---

## ✅ En producción — v0.16.0

Corriendo 24/7 en Servidor Madre (Linux) con Docker desde 24 abril 2026.

- 9 comandos: `/start` `/nueva` `/citas` `/habito` `/habitos` `/semana` `/resumen` `/config` `/cancelar`
- NLP con texto libre vía Groq (Llama 3.1) — latencia ~300ms
- Detección de conflictos de agenda
- Vista semanal navegable
- Scheduler: resumen diario + avisos de citas + evening log
- Separación estricta API/bot: el bot nunca accede a la DB directamente
- Tests con pytest + pytest-asyncio
- Deploy con Docker + docker-compose

---

## 🟠 Pendiente merge — v0.17.0

Rama: `feature/v0.17.0-nlp-llm-multiuser`

| Feature | Descripción |
|---|---|
| **LLMBackend factory** | GroqBackend + OllamaBackend intercambiables — preparado para fallback local |
| **NLP mejorado** | Contexto conversacional enriquecido en las llamadas al LLM |
| **Multiusuario** | Migraciones Alembic + `user_id` en todos los modelos SQLite y endpoints |
| **Handler /diario** | Escribe entradas de diario en yggdrasil-dew vía GitHub Contents API |
| **github_client.py** | Cliente para integración con yggdrasil-dew (GitHub Contents API) |
| **pydantic-settings** | Config centralizada con `GITHUB_TOKEN` y validación de entorno |

### Pasos para el merge
- [ ] Añadir secrets en GitHub Actions (`GITHUB_TOKEN`, `GROQ_API_KEY`, etc.)
- [ ] `alembic upgrade head` en Servidor Madre
- [ ] `pytest tests/unit/bot/ -v` en local
- [ ] Eliminar `tests.yml` workflow obsoleto

---

## 🔵 Planificado — v0.18+

El detalle de sprints, criterios y prioridades vive en [yggdrasil-dew/proyectos/thdora.md](https://github.com/alvarofernandezmota-tech/yggdrasil-dew/blob/main/proyectos/thdora.md).

Líneas planificadas en orden aproximado:

- Notas de voz (Whisper vía Groq)
- Historial conversacional NLP persistente entre reinicios
- CD automático GitHub Actions → Madre por SSH
- Fallback automático Ollama → Groq
- Soporte multiusuario completo con gestión desde bot
- Capa regex NLP nivel 0 (intenciones simples sin LLM)
- Extracción de `thdora-base` como módulo reutilizable
- RAG sobre yggdrasil-dew (Open WebUI + Ollama)
- PostgreSQL en Servidor Madre

---

_Última actualización: 17 jun 2026 — v0.16.0 en producción · v0.17.0 pendiente merge_
