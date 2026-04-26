# THDORA — Asistente Personal de Gestión de Vida

> Bot de Telegram + API REST para gestionar citas, hábitos y notificaciones diarias.  
> Construido con Python, FastAPI y python-telegram-bot v22.

[![Tests](https://github.com/alvarofernandezmota-tech/thdora/actions/workflows/tests.yml/badge.svg)](https://github.com/alvarofernandezmota-tech/thdora/actions/workflows/tests.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Parte del ecosistema

> THDORA es el **producto** del tridente. Se construye con `ai-toolkit` y se documenta en `personal`.

| Repo | Rol |
|------|-----|
| 🏠 [personal](https://github.com/alvarofernandezmota-tech/personal) | OS personal — tracking, contexto, hoja de ruta |
| 🤖 [ai-toolkit](https://github.com/alvarofernandezmota-tech/ai-toolkit) | Stack IA — Claude Code + OpenRouter + Ollama |
| 💬 **thdora** (este repo) | El producto — bot Telegram + FastAPI |

---

## ¿Qué es THDORA?

THDORA es un sistema personal de productividad accesible desde Telegram. El usuario puede crear citas,
registrar hábitos diarios y recibir notificaciones automáticas — todo a través de texto libre procesado
por un LLM (Groq/Llama) o mediante flujos guiados por botones.

El sistema detecta conflictos de agenda con solapamiento real de bloques horarios, genera horarios
visuales por franjas y permite navegar entre semanas desde el propio chat.

**Estado actual:** ✅ Corriendo 24/7 en servidor con Docker desde 24 abril 2026.

---

## Stack técnico

| Capa | Tecnología | Por qué |
|---|---|---|
| **API REST** | FastAPI + Pydantic v2 | Validación de tipos, OpenAPI automático, async nativo |
| **Base de datos** | SQLite + SQLAlchemy 2.x | Sin servidor, ideal para despliegue en VPS single-node |
| **Bot** | python-telegram-bot v22 | API async, ConversationHandler para flujos multi-paso |
| **NLP / intent** | Groq (Llama 3) | Latencia baja (~300ms), gratis en tier dev, JSON estructurado |
| **Scheduler** | APScheduler 3.x | Jobs persistentes para recordatorios y resúmenes diarios |
| **Tests** | pytest + pytest-asyncio | Cobertura de lógica pura sin dependencias externas |
| **CI** | GitHub Actions | Lint (flake8) + tests en cada push, badge en README |
| **Deploy** | Docker + docker-compose | Reproducible en cualquier VPS, separación API/bot en servicios |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│  Usuario (Telegram)                                     │
└────────────────────┬────────────────────────────┘
                     │ Mensaje texto / botón
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Bot  (python-telegram-bot v22)                         │
│  ├── handlers/nlp.py    ← texto libre → Groq → intent   │
│  ├── handlers/citas.py  ← flujo guiado multi-paso       │
│  ├── handlers/habitos.py                                │
│  ├── handlers/semana.py ← vista semanal (2 req paralelo) │
│  └── scheduler.py       ← APScheduler jobs diarios      │
└────────────────────┬────────────────────────────┘
                     │ HTTP (httpx async)
                     ▼
┌─────────────────────────────────────────────────────────┐
│  API REST  (FastAPI + Uvicorn)                          │
│  ├── /appointments  ← CRUD + conflicto solapamiento 1h  │
│  ├── /habits        ← CRUD + acumulación                │
│  ├── /config        ← hábitos configurados + notifs     │
│  └── /summary       ← resumen diario                    │
└────────────────────┬────────────────────────────┘
                     │ SQLAlchemy ORM
                     ▼
              SQLite  (datos/thdora.db)
```

---

## Decisiones de diseño destacadas

- **Solapamiento real de citas**: el endpoint `GET /appointments/{date}/conflict/{time}` usa la fórmula
  `new_start < exist_end AND new_end > exist_start` en vez de comparar hora exacta.

- **Vista semanal optimizada**: `semana.py` pasó de 14 llamadas HTTP en serie a 2 concurrentes usando
  `asyncio.gather` + el endpoint `/appointments/week/{date}`.

- **NLP con fallback visual**: cuando Groq extrae `time=00:00` o hay conflicto, el bot genera un
  horario visual con franjas de 30min (08:00–22:00) marcando bloques ocupados.

- **Separación API/bot**: la API expone el dominio completo; el bot es un cliente HTTP puro.

---

## Estructura del proyecto

```
thdora/
├── src/
│   ├── api/                  # FastAPI — endpoints REST
│   │   ├── routers/          # appointments, habits, config, user_config
│   │   └── models/           # modelos Pydantic + SQLAlchemy
│   └── bot/                  # Bot Telegram
│       ├── main.py           # Entrypoint, registro de handlers
│       ├── api_client.py     # Cliente HTTP async (httpx)
│       ├── groq_router.py    # Enrutador NLP: texto → intent + datos
│       ├── scheduler.py      # APScheduler: resumen, evening log, recordatorios
│       ├── keyboards.py      # Teclados inline centralizados
│       └── handlers/
│           ├── citas.py      # /nueva, /citas, editar, borrar
│           ├── habitos.py    # /habito, /habitos, editar, borrar
│           ├── config.py     # /config: hábitos + notificaciones
│           ├── semana.py     # /semana + navegación semanal
│           ├── nlp.py        # Texto libre → Groq → acción
│           └── common.py     # /cancelar, /resumen, error_handler
├── tests/
├── docs/
├── CHANGELOG.md
├── ROADMAP.md
├── Makefile
├── Dockerfile
└── docker-compose.yml
```

---

## Instalación y arranque

```bash
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora
cp .env.example .env
# Editar .env con TELEGRAM_BOT_TOKEN y GROQ_API_KEY
pip install -e ".[dev]"

make run-api   # FastAPI en http://localhost:8000
make run-bot   # Bot Telegram

# O con Docker (producción)
make docker-up
```

---

## Tests

```bash
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Comandos del bot

| Comando | Descripción |
|---|---|
| `/start` | Menú principal + programar jobs diarios |
| `/nueva` | Crear cita con flujo guiado |
| `/citas` | Ver y gestionar citas de hoy |
| `/habito` | Registrar un hábito con botones rápidos |
| `/habitos` | Ver hábitos del día |
| `/semana` | Vista semanal navegable |
| `/resumen` | Resumen del día (citas + hábitos) |
| `/config` | Configurar hábitos y notificaciones |
| `/cancelar` | Cancelar cualquier flujo activo |

También acepta **texto libre**: _"mañana dentista a las 5"_, _"dormí 7 horas"_, _"cancela el gym de hoy"_.

---

## 🚧 Roadmap (por orden de dependencia)

| Issue | Feature | Estado |
|-------|---------|--------|
| [#10](https://github.com/alvarofernandezmota-tech/thdora/issues/10) | 🐛 Fix `/config` timeout | 🔴 Bug — aplicar ya (3 líneas) |
| [#3](https://github.com/alvarofernandezmota-tech/thdora/issues/3) | F10 Multi-usuario | 🔴 Prioritario — todo depende de esto |
| [#4](https://github.com/alvarofernandezmota-tech/thdora/issues/4) | F11 Scheduler notificaciones | 🟠 Requiere F10 |
| [#2](https://github.com/alvarofernandezmota-tech/thdora/issues/2) | F9.4 UX citas + vista mes | 🟠 Requiere F10 |
| [#9](https://github.com/alvarofernandezmota-tech/thdora/issues/9) | F16 Onboarding + perfil usuario | 🟡 Requiere F10 |
| [#5](https://github.com/alvarofernandezmota-tech/thdora/issues/5) | F12 IA lenguaje natural (Groq) | 🟡 Requiere F10 |
| [#6](https://github.com/alvarofernandezmota-tech/thdora/issues/6) | F13 Análisis hábitos con IA | 🟢 Requiere F12 |
| [#8](https://github.com/alvarofernandezmota-tech/thdora/issues/8) | F15 Voz a texto (Whisper) | 🟢 Requiere F12 |
| [#7](https://github.com/alvarofernandezmota-tech/thdora/issues/7) | F14 Llamada Twilio urgente | 🔵 Futuro |

---

## Versión actual

**v4.1.0** — 2026-04-26  
Desplegado en servidor con Docker. Corriendo 24/7.

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo.  
Ver [ROADMAP.md](ROADMAP.md) para próximas funcionalidades.

---

*Construido y mantenido por [Álvaro Fernández Mota](https://github.com/alvarofernandezmota-tech) · Actualizado 26 abril 2026*
