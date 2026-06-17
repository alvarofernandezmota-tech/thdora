# THDORA — Contexto para LLMs

> Lee este archivo. Luego lee los archivos que necesites vía los raw links de `llms.txt`.
> Idioma de trabajo: **español siempre**.

---

## Stack

- Python 3.11 · python-telegram-bot v20+ · FastAPI · SQLite · httpx async
- pydantic-settings · APScheduler · Groq (`llama-3.3-70b-versatile`) · Ollama (preparado)
- GitHub Contents API (diario en [yggdrasil-dew](https://github.com/alvarofernandezmota-tech/yggdrasil-dew))
- Docker (2 contenedores: `api` + `bot`) sobre servidor Arch Linux **Madre**

---

## Estructura clave

```
src/
├── config.py                        # Todas las variables de entorno (pydantic-settings)
├── bot/
│   ├── main.py                        # Entrypoint bot v4.5 — registra todos los handlers
│   ├── groq_router.py                 # NLP: intent + function calling + transcribe()
│   ├── http_client.py                 # Singleton httpx compartido
│   ├── api_client.py                  # Cliente FastAPI interna
│   ├── middleware.py                  # @require_allowed_user
│   ├── scheduler.py                   # APScheduler — resumen diario + avisos
│   └── handlers/
│       ├── nlp.py                     # Texto libre → GroqRouter
│       ├── diario.py                  # /diario → yggdrasil-dew
│       ├── citas.py                   # /nueva, editar, borrar citas
│       ├── habitos.py                 # /habito, registrar hábitos
│       ├── onboarding.py              # /start, /onboarding
│       ├── stats.py                   # /stats
│       ├── nlp_disambig.py            # Desambiguación NLP inline
│       └── config.py (handler)        # /config
└── services/
    └── github_client.py               # GitHub Contents API — append_to_diario()
```

---

## Estado actual — v0.17.0 (17 jun 2026)

✅ **En producción en Madre** desde 14 jun 2026.

### Funciona hoy
- 10 comandos: `/start` `/citas` `/habitos` `/habito` `/nueva` `/semana` `/resumen` `/config` `/cancelar` `/diario` `/stats`
- NLP texto libre → Groq → function calling (crear/consultar/borrar citas)
- `/diario` guarda entradas en yggdrasil-dew vía GitHub Contents API
- Scheduler: resumen diario + evening log + avisos de citas
- Persistencia SQLite + PicklePersistence (contexto NLP sobrevive reinicios)
- Control de acceso `@require_allowed_user` en todos los handlers sensibles

### Sprint 2 — mergeado hoy
- `http_client.py`: singleton httpx con connection pooling
- `groq_router.py`: `@lru_cache` en system prompt + 256 tokens + `transcribe()` (Whisper)
- `middleware.py`: `@require_allowed_user` reutilizable
- `main.py` v4.5: `PicklePersistence(update_interval=60)` + `post_shutdown`
- `nlp.py`: TYPING + filtro triviales + maneja `ToolCallResult`/`AmbiguityRequest`

---

## Tareas pendientes (por orden de impacto)

| # | Tarea | Esfuerzo |
|---|-------|----------|
| 1 | `conversation_timeout=300` en los 6 `ConversationHandler` factories | 10 min |
| 2 | `docker-compose.yml` healthcheck real: `pgrep -f entrypoint-bot.sh` | 5 min |
| 3 | Añadir `GITHUB_TOKEN` a `.env` en Madre + secrets GitHub Actions | 15 min |
| 4 | Probar `/diario` end-to-end en Madre | 5 min |
| 5 | Historial conversación real: pasar `nlp_history` a Groq como mensajes | 1h |
| 6 | `voice.py`: notas de voz con Whisper (`transcribe()` ya está en `groq_router.py`) | 45 min |
| 7 | Resumen semanal inteligente: SQL sobre datos propios + Groq | 2h |
| 8 | CD automático GitHub Actions → Madre | 2h |
| 9 | Arquitectura 3 niveles NLP: regex → Ollama 3b → Groq 70b | 1 día |
| 10 | Multiusuario real: `user_id` en todos los endpoints API | 3h |

---

## Reglas de trabajo

1. **Leer antes de tocar** — siempre fetch del raw actual antes de modificar un archivo
2. **Archivo completo** — nunca entregar diffs, siempre el archivo entero
3. **Sin inventar** — si no tienes el archivo, pídelo antes de escribir código
4. **Rama activa**: `main` (Sprint 2 ya mergeado)
5. **Idioma**: español siempre

---

> Repo: https://github.com/alvarofernandezmota-tech/thdora
> ROADMAP completo: https://raw.githubusercontent.com/alvarofernandezmota-tech/thdora/main/ROADMAP.md
> Última actualización: 17 jun 2026 — 02:23 CEST
