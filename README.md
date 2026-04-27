# THDORA — Asistente Personal de Gestión de Vida

> Bot de Telegram + API REST para gestionar citas, hábitos y notificaciones diarias.  
> Construido con Python 3.12, FastAPI y python-telegram-bot v22.

[![Tests](https://github.com/alvarofernandezmota-tech/thdora/actions/workflows/tests.yml/badge.svg)](https://github.com/alvarofernandezmota-tech/thdora/actions/workflows/tests.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-24%2F7-2496ED?logo=docker)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Estado:** ✅ Corriendo 24/7 en servidor con Docker desde 24 abril 2026 · **v0.16.0**

---

## ¿Qué es THDORA?

THDORA es un asistente personal accesible desde Telegram. Puedes crear citas, registrar hábitos diarios y recibir notificaciones automáticas — mediante texto libre procesado por Groq/Llama o flujos guiados por botones.

Detecta conflictos de agenda, genera vistas semanales navegables y permite gestionar tu día desde el chat sin abrir ninguna app.

---

## Quick start

```bash
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora
cp .env.example .env          # añade TELEGRAM_BOT_TOKEN y GROQ_API_KEY
make docker-up                # arranca API + Bot en Docker
```

O en local para desarrollo:

```bash
pip install -e ".[dev]"
make run-api    # FastAPI en http://localhost:8000
make run-bot    # Bot Telegram
```

---

## Stack técnico

| Capa | Tecnología | Por qué |
|---|---|---|
| **API REST** | FastAPI + Pydantic v2 | Validación de tipos, OpenAPI en `/docs`, async nativo |
| **Base de datos** | SQLite + SQLAlchemy 2.x | Sin servidor, ideal para VPS single-node |
| **Bot** | python-telegram-bot v22 | ConversationHandler para flujos multi-paso |
| **NLP / intent** | Groq (Llama 3.1) | ~300ms latencia, tier gratuito, JSON estructurado |
| **Scheduler** | APScheduler 3.x | Resumen diario + evening log + avisos de citas |
| **Tests** | pytest + pytest-asyncio | Cobertura sin dependencias externas |
| **Deploy** | Docker + docker-compose | API y bot como servicios independientes |

---

## Arquitectura

```
┌──────────────────────────────────────────────┐
│  Usuario (Telegram)                          │
└─────────────────┬────────────────────────────┘
                  │ Mensaje texto / botón
                  ▼
┌──────────────────────────────────────────────┐
│  Bot  (python-telegram-bot v22)              │
│  ├── handlers/nlp.py    ← texto libre→Groq   │
│  ├── handlers/citas.py  ← flujo multi-paso   │
│  ├── handlers/habitos.py                     │
│  ├── handlers/semana.py ← vista semanal      │
│  └── scheduler.py       ← APScheduler jobs  │
└─────────────────┬────────────────────────────┘
                  │ HTTP (httpx async)
                  ▼
┌──────────────────────────────────────────────┐
│  API REST  (FastAPI + Uvicorn)               │
│  ├── /appointments  ← CRUD + conflictos      │
│  ├── /habits        ← CRUD + acumulación     │
│  └── /summary       ← resumen diario         │
└─────────────────┬────────────────────────────┘
                  │ SQLAlchemy ORM
                  ▼
           SQLite  (data/thdora.db)
```

**Principio clave:** el bot nunca accede a la DB directamente. Solo habla con la API. Esto permite escalar ambas capas por separado.

---

## Estructura del proyecto

```
thdora/
├── src/
│   ├── api/                  # FastAPI — endpoints REST
│   │   ├── routers/          # appointments, habits, summary
│   │   └── deps.py           # inyección de dependencias
│   └── bot/                  # Bot Telegram
│       ├── main.py           # Entrypoint, registro de handlers
│       ├── api_client.py     # Cliente HTTP async (httpx)
│       ├── groq_router.py    # NLP: texto → intent + datos
│       ├── scheduler.py      # APScheduler: resumen, evening, recordatorios
│       ├── keyboards.py      # Teclados inline centralizados
│       └── handlers/
│           ├── citas.py      # /nueva, /citas, editar, borrar
│           ├── habitos.py    # /habito, /habitos, editar, borrar
│           ├── config.py     # /config: hábitos + notificaciones
│           ├── semana.py     # /semana + navegación semanal
│           ├── nlp.py        # Texto libre → Groq → acción
│           └── common.py     # /cancelar, /resumen, error_handler
├── tests/                    # pytest — unitarios + integración
├── docs/                     # Arquitectura, diarios, API reference
├── CHANGELOG.md
├── ROADMAP.md
├── Makefile                  # make run-api / run-bot / test / docker-up
├── Dockerfile
└── docker-compose.yml
```

---

## Comandos del bot

| Comando | Descripción |
|---|---|
| `/start` | Menú principal + programar jobs diarios |
| `/nueva` | Crear cita con flujo guiado (franjas + hora + nombre + tipo) |
| `/citas` | Ver y gestionar citas del día |
| `/habito` | Registrar hábito con botones rápidos |
| `/habitos` | Ver hábitos del día |
| `/semana` | Vista semanal navegable |
| `/resumen` | Resumen del día (citas + hábitos) |
| `/config` | Configurar tipos de hábitos y notificaciones |
| `/cancelar` | Cancelar cualquier flujo activo |

También acepta **texto libre**: _"mañana dentista a las 5"_, _"dormí 7 horas"_, _"¿qué tengo esta semana?"_

---

## Tests

```bash
pytest tests/ -v                                    # todos los tests
pytest tests/unit/ -v                               # solo unitarios
pytest tests/ --cov=src --cov-report=term-missing   # con cobertura
```

---

## Decisiones de diseño

- **Separación API/bot:** la API expone el dominio completo; el bot es un cliente HTTP puro. Permite escalar, testear y desplegar por separado.
- **AbstractLifeManager:** abstracción sobre la DB que permite migrar de SQLite a PostgreSQL cambiando solo una clase.
- **Solapamiento real de citas:** `new_start < exist_end AND new_end > exist_start` — no compara hora exacta.
- **NLP con contexto:** el system prompt de Groq incluye citas y hábitos de hoy/mañana, permitiendo respuestas con datos reales.
- **3 llamadas en paralelo:** `asyncio.gather` para obtener contexto API sin latencia adicional.

---

## Parte del ecosistema

| Repo | Rol |
|------|-----|
| 🏠 [personal](https://github.com/alvarofernandezmota-tech/personal) | OS personal — tracking, contexto, hoja de ruta |
| 🤖 [ai-toolkit](https://github.com/alvarofernandezmota-tech/ai-toolkit) | Stack IA — agentes, OpenRouter, Ollama |
| 💬 **thdora** (este repo) | El producto — bot Telegram + FastAPI |

---

Ver [CHANGELOG.md](CHANGELOG.md) · [ROADMAP.md](ROADMAP.md) · [Arquitectura detallada](docs/ARCHITECTURE.md)

*Construido y mantenido por [Álvaro Fernández Mota](https://github.com/alvarofernandezmota-tech) · v0.16.0 · 27 abril 2026*
