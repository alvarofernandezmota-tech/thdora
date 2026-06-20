# 🗺️ THDORA — ROADMAP

Navegación rápida: [README](README.md) · [CHANGELOG](CHANGELOG.md)

El roadmap detallado de versiones futuras (v0.18+) vive en [yggdrasil-dew/proyectos/thdora.md](https://github.com/alvarofernandezmota-tech/yggdrasil-dew/blob/main/proyectos/thdora.md).

---

## ✅ En main — v0.17.0 (2026-06-20)

Todos los bugs B12–B25 corregidos. Stack Docker completamente funcional.

### Correcciones v0.17.0
- **14 bugs críticos** B12–B25 corregidos (ver [CHANGELOG](CHANGELOG.md))
- `user_id` obligatorio en todos los métodos de `ThdoraApiClient`
- Firmas de API unificadas: `(data:dict, user_id)` en create/update/upsert
- Funciones truncadas completadas: `cb_hab_edit_field`, `_do_edit_habit`, handlers
- PTB ≥20 compat: `update.get_bot()` → `context.bot`
- Dockerfile multi-stage + usuario no-root
- `docker/entrypoint.sh` unificado con `SERVICE_TARGET` env var
- `docker-compose.yml` corregido: servicios independientes, healthcheck real
- CI/CD: `.github/workflows/ci.yml` + `docker-health.yml`
- Tests: suite completa `tests/` con pytest-asyncio + AsyncMock
- `scripts/autotest.py`: verificación del ecosistema sin pytest
- Docs: `ARCHITECTURE.md`, `CONTRIBUTING.md`, `docs/ADR-001`, `docs/ADR-002`, `llms.txt`

### Para hacer antes del deploy en Servidor Madre
- [ ] Añadir secrets en GitHub Actions (`TELEGRAM_TOKEN`, `GROQ_API_KEY`, etc.)
- [ ] `git pull && docker compose build --no-cache && docker compose up -d`
- [ ] Verificar logs: `docker compose logs -f thdora` → alembic OK + uvicorn OK
- [ ] Verificar logs: `docker compose logs -f bot` → PTB polling OK
- [ ] Smoke test: `/start` → `/citas` → texto libre en Telegram

---

## ✅ En producción — v0.16.0 (desde 24 abril 2026)

- 9 comandos: `/start` `/nueva` `/citas` `/habito` `/habitos` `/semana` `/resumen` `/config` `/cancelar`
- NLP con texto libre vía Groq (Llama 3.1) — latencia ~300ms
- Detección de conflictos de agenda
- Vista semanal navegable
- Scheduler: resumen diario + avisos de citas + evening log
- Separación estricta API/bot
- Deploy Docker + docker-compose

---

## 🔵 Planificado — v0.18+

En orden aproximado de prioridad:

- **LLMBackend factory**: GroqBackend + OllamaBackend intercambiables con fallback local
- **NLP mejorado**: contexto conversacional persistente entre reinicios
- **Handler /diario**: entradas de diario en yggdrasil-dew vía GitHub Contents API
- **`github_client.py`**: cliente para integración con yggdrasil-dew
- **CD automático**: GitHub Actions → Servidor Madre por SSH
- **Fallback Ollama→Groq**: automático si Groq no responde
- **Multiusuario completo**: gestión de usuarios desde el bot
- **Capa regex NLP nivel 0**: intenciones simples sin LLM (latencia ~0ms)
- **PostgreSQL**: migración de SQLite a Postgres en Servidor Madre
- **RAG sobre yggdrasil-dew**: Open WebUI + Ollama

---

_Última actualización: 2026-06-20 — v0.17.0 en main · Deploy pendiente en Servidor Madre_
