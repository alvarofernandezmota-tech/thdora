# THDORA / TOKI — Asistente Personal de Gestión de Vida

> Bot de Telegram + API REST para gestionar citas, hábitos, diario y notificaciones diarias.
> Construido con Python 3.12, FastAPI y python-telegram-bot v22.

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-24%2F7-2496ED?logo=docker)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Estado:** ✅ Corriendo 24/7 en Servidor Madre con Docker · **v0.17.0** (pendiente merge a main)

---

## ¿Qué es THDORA / TOKI?

THDORA es un asistente personal accesible desde Telegram. El asistente se llama **TOKI**.
Puedes crear citas, registrar hábitos, escribir tu diario y recibir notificaciones automáticas — mediante texto libre procesado por Groq/Llama o flujos guiados por botones.

Detecta conflictos de agenda, genera vistas semanales navegables y permite gestionar tu día desde el chat sin abrir ninguna app.

---

## Contexto del proyecto

El diario de desarrollo, decisiones de arquitectura y estado real del proyecto viven en el segundo cerebro:

> 🧠 **[yggdrasil-dew](https://github.com/alvarofernandezmota-tech/yggdrasil-dew)** — fuente de verdad del ecosistema
> - Estado thdora: [proyectos/thdora.md](https://github.com/alvarofernandezmota-tech/yggdrasil-dew/blob/main/proyectos/thdora.md)
> - Diario: [diarios/](https://github.com/alvarofernandezmota-tech/yggdrasil-dew/tree/main/diarios)

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
| **Base de datos** | SQLite + SQLAlchemy 2.x + Alembic | Sin servidor, migraciones, preparado para PostgreSQL |
| **Bot** | python-telegram-bot v22 | ConversationHandler para flujos multi-paso |
| **NLP / intent** | Groq (Llama 3.1) + Ollama local | ~300ms latencia, fallback local |
| **Scheduler** | APScheduler 3.x | Resumen diario + evening log + avisos de citas |
| **Tests** | pytest + pytest-asyncio | Cobertura sin dependencias externas |
| **Deploy** | Docker + docker-compose + GitHub Actions | CI/CD automático a Servidor Madre |

---

## Arquitectura

```
┌────────────────────────────────────────────┐
│  Usuario (Telegram)                          │
└─────────────────┤────────────────────────┘
                  │ Mensaje texto / botón
                  ▼
┌────────────────────────────────────────────┐
│  Bot  (python-telegram-bot v22)              │
│  ├── handlers/nlp.py    ← texto libre→Groq   │
│  ├── handlers/citas.py  ← flujo multi-paso   │
│  ├── handlers/habitos.py                     │
│  ├── handlers/semana.py ← vista semanal      │
│  ├── handlers/diario.py ← escribe en ygg     │
│  └── scheduler.py       ← APScheduler jobs  │
└───────────────┤────────────────────────┘
                  │ HTTP (httpx async)
                  ▼
┌────────────────────────────────────────────┐
│  API REST  (FastAPI + Uvicorn)               │
│  ├── /appointments  ← CRUD + conflictos      │
│  ├── /habits        ← CRUD + acumulación     │
│  └── /summary       ← resumen diario         │
└───────────────┤────────────────────────┘
                  │ SQLAlchemy ORM
                  ▼
           SQLite  (data/thdora.db)
                  │
                  ▼ (planificado)
           PostgreSQL (Servidor Madre)
```

---

## Comandos del bot

| Comando | Descripción |
|---|---|
| `/start` | Menú principal + programar jobs diarios |
| `/nueva` | Crear cita con flujo guiado |
| `/citas` | Ver y gestionar citas del día |
| `/habito` | Registrar hábito con botones rápidos |
| `/habitos` | Ver hábitos del día |
| `/semana` | Vista semanal navegable |
| `/resumen` | Resumen del día (citas + hábitos) |
| `/config` | Configurar tipos de hábitos y notificaciones |
| `/diario` | Escribir entrada en yggdrasil-dew via GitHub API |
| `/stats` | Estadísticas personales |
| `/tiempo` | Estado del tiempo |
| `/cancelar` | Cancelar cualquier flujo activo |

También acepta **texto libre**: _"mañana dentista a las 5"_, _"dormí 7 horas"_, _"¿qué tengo esta semana?"_

---

## Estructura del proyecto

```
thdora/
├── src/
│   ├── api/              # FastAPI — endpoints REST
│   ├── ai/               # LLMBackend: Groq + Ollama + Factory
│   ├── bot/              # Handlers Telegram
│   │   ├── handlers/
│   │   │   ├── citas.py
│   │   │   ├── habitos.py
│   │   │   ├── semana.py
│   │   │   ├── nlp.py
│   │   │   └── diario.py   # ← escribe en yggdrasil-dew
│   │   ├── api_client.py
│   │   └── scheduler.py
│   ├── core/             # lógica de negocio
│   └── db/               # SQLAlchemy + Alembic (multiusuario)
├── .github/workflows/
│   └── deploy.yml        # CI/CD → Servidor Madre
├── docker-compose.yml · Dockerfile · Makefile
├── pyproject.toml · requirements.txt · .env.example
├── CHANGELOG.md
└── ROADMAP.md
```

---

## Tests

```bash
pytest tests/ -v
pytest tests/unit/bot/ -v
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Decisiones de diseño

- **Separación API/bot:** la API expone el dominio completo; el bot es un cliente HTTP puro.
- **AbstractLifeManager:** abstracción sobre la DB que permite migrar de SQLite a PostgreSQL cambiando solo una clase.
- **LLMBackend factory:** `GroqBackend` + `OllamaBackend` — intercambiables, fallback local.
- **Solapamiento real de citas:** `new_start < exist_end AND new_end > exist_start`.
- **NLP con contexto:** el system prompt incluye citas y hábitos de hoy/mañana.
- **Multiusuario:** Alembic migrations, modelos con `user_id`, aislamiento total de datos.

---

## Parte del ecosistema

| Repo | Rol |
|------|-----|
| 🧠 [yggdrasil-dew](https://github.com/alvarofernandezmota-tech/yggdrasil-dew) | **Second brain** — fuente de verdad, diario, estado del proyecto |
| 🤖 [ai-toolkit](https://github.com/alvarofernandezmota-tech/ai-toolkit) | Stack IA — agentes, Ollama, herramientas dev |
| 💬 **thdora** (este repo) | El producto — bot Telegram + FastAPI |

---

Ver [CHANGELOG.md](CHANGELOG.md) · [ROADMAP.md](ROADMAP.md)

*Construido y mantenido por [Álvaro Fernández Mota](https://github.com/alvarofernandezmota-tech) · v0.17.0 · 17 junio 2026*
