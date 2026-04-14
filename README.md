# THDORA — Asistente Personal de Gestión de Vida

> Bot de Telegram + API REST para gestionar citas, hábitos y notificaciones diarias.  
> Construido con Python, FastAPI y python-telegram-bot v22.

[![Tests](https://github.com/alvarofernandezmota-tech/thdora/actions/workflows/tests.yml/badge.svg)](https://github.com/alvarofernandezmota-tech/thdora/actions/workflows/tests.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ¿Qué es THDORA?

THDORA es un sistema personal de productividad accesible desde Telegram. El usuario puede crear citas,
registrar hábitos diarios y recibir notificaciones automáticas — todo a través de texto libre procesado
por un LLM (Groq/Llama) o mediante flujos guiados por botones.

El sistema detecta conflictos de agenda con solapamiento real de bloques horarios, genera horarios
visuales por franjas y permite navegar entre semanas desde el propio chat.

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
└────────────────────┬────────────────────────────────────┘
                     │ Mensaje texto / botón
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Bot  (python-telegram-bot v22)                         │
│  ├── handlers/nlp.py    ← texto libre → Groq → intent   │
│  ├── handlers/citas.py  ← flujo guiado multi-paso       │
│  ├── handlers/habitos.py                                │
│  ├── handlers/semana.py ← vista semanal (2 req paralelo) │
│  └── scheduler.py       ← APScheduler jobs diarios      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP (httpx async)
                     ▼
┌─────────────────────────────────────────────────────────┐
│  API REST  (FastAPI + Uvicorn)                          │
│  ├── /appointments  ← CRUD + conflicto solapamiento 1h  │
│  ├── /habits        ← CRUD + acumulación                │
│  ├── /config        ← hábitos configurados + notifs     │
│  └── /summary       ← resumen diario                    │
└────────────────────┬────────────────────────────────────┘
                     │ SQLAlchemy ORM
                     ▼
              SQLite  (datos/thdora.db)
```

---

## Decisiones de diseño destacadas

- **Solapamiento real de citas**: el endpoint `GET /appointments/{date}/conflict/{time}` usa la fórmula
  `new_start < exist_end AND new_end > exist_start` en vez de comparar hora exacta. Cubre los 4 casos
  de solapamiento (inicio, fin, dentro, exacta) con duración configurable vía query param `?duration=`.

- **Vista semanal optimizada**: `semana.py` pasó de 14 llamadas HTTP en serie a 2 concurrentes usando
  `asyncio.gather` + el endpoint `/appointments/week/{date}`.

- **NLP con fallback visual**: cuando Groq extrae `time=00:00` (hora no detectada) o hay conflicto,
  el bot genera un horario visual con franjas de 30min (08:00–22:00) marcando bloques ocupados.

- **Separación API/bot**: la API expone el dominio completo; el bot es un cliente HTTP puro. Permite
  usar la API desde cualquier otro cliente (web, móvil) sin tocar el bot.

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
│   └── unit/
│       ├── test_appointments_overlap.py   # _find_overlap, _time_to_minutes
│       ├── test_json_lifemanager.py       # JsonLifeManager
│       ├── test_memory_lifemanager.py     # MemoryLifeManager
│       └── bot/
│           └── test_nlp_schedule.py       # _build_day_schedule, _end_time
├── docs/                     # Documentación técnica extendida
├── CHANGELOG.md
├── ROADMAP.md
├── Makefile
├── Dockerfile
└── docker-compose.yml
```

---

## Instalación y arranque

```bash
# 1. Clonar y entrar
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora

# 2. Variables de entorno
cp .env.example .env
# Editar .env con TELEGRAM_BOT_TOKEN y GROQ_API_KEY

# 3. Instalar dependencias
pip install -e ".[dev]"

# 4. Arrancar API y bot por separado
make run-api   # FastAPI en http://localhost:8000
make run-bot   # Bot Telegram

# O con Docker
make docker-up
```

---

## Tests

```bash
# Todos los tests
pytest tests/ -v

# Solo unitarios (sin API ni bot levantado)
pytest tests/unit/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Comandos del bot

| Comando | Descripción |
|---|---|
| `/start` | Menú principal + programar jobs diarios |
| `/nueva` | Crear cita con flujo guiado (fecha → franja → hora → tipo) |
| `/citas` | Ver y gestionar citas de hoy |
| `/habito` | Registrar un hábito con botones rápidos |
| `/habitos` | Ver hábitos del día |
| `/semana` | Vista semanal navegable |
| `/resumen` | Resumen del día (citas + hábitos) |
| `/config` | Configurar hábitos y notificaciones |
| `/cancelar` | Cancelar cualquier flujo activo |

También acepta **texto libre**: _"mañana dentista a las 5"_, _"dormí 7 horas"_, _"cancela el gym de hoy"_.

---

## Versión actual

**v4.1.0** — 2026-04-14

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo.  
Ver [ROADMAP.md](ROADMAP.md) para próximas funcionalidades.
