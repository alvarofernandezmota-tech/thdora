# 🧠 THDORA

> **Tu asistente personal de gestión de vida — Bot Telegram + FastAPI + SQLite + IA (próximamente)**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57)](https://sqlite.org)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-21%2B-2CA5E0)](https://python-telegram-bot.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ¿Qué es THDORA?

THDORA es un ecosistema de **gestión personal** que vive en Telegram. Registra citas, hábitos diarios y genera resúmenes — todo desde el móvil, sin abrir ningún app extra.

Los datos se guardan en **SQLite local** (persisten entre reinicios) y se exponen a través de una **API REST** con FastAPI. En el futuro próximo: gamificación RPG y procesamiento con IA local.

---

## ✨ Funcionalidades actuales (v0.8.0)

### Bot Telegram

| Comando | Descripción |
|---------|-------------|
| `/start` | Bienvenida y lista de comandos |
| `/nueva` | Crear cita en 5 pasos (fecha → hora → nombre → tipo → notas) |
| `/citas [fecha]` | Ver citas del día con botones inline Borrar/Editar |
| `/habito` | Registrar hábito rápido con teclado + acumulación `+N` |
| `/habitos [fecha]` | Ver hábitos del día con botones inline |
| `/resumen [fecha]` | Resumen completo: citas + hábitos |
| `/cancelar` | Cancelar cualquier operación en curso |

**Fechas aceptadas:** `hoy`, `mañana`, `ayer`, `27/03`, `2026-03-27`, `lunes`, `el viernes`…

**Hábitos acumulables:** escribe `+2` para sumar al valor existente, o el valor directo para sobreescribir.

### API REST (FastAPI)

```
Citas:
  POST   /appointments/{date}                → crear cita
  GET    /appointments/{date}                → citas del día
  GET    /appointments/week/{date}           → citas de la semana (lun–dom)
  GET    /appointments/range/{from}/{to}     → citas en rango
  GET    /appointments/upcoming/{date}       → próximas citas
  PUT    /appointments/{date}/{index}        → editar cita
  DELETE /appointments/{date}/{index}        → borrar cita

Hábitos:
  POST   /habits/{date}                      → registrar hábito (upsert)
  GET    /habits/{date}                      → hábitos del día
  GET    /habits/week/{date}                 → hábitos de la semana
  GET    /habits/range/{from}/{to}           → hábitos en rango
  GET    /habits/stats/{habit}?days=30       → historial de un hábito
  PUT    /habits/{date}/{habit}              → actualizar valor
  DELETE /habits/{date}/{habit}              → borrar hábito

Resumen:
  GET    /summary/{date}                     → citas + hábitos del día
  GET    /summary/week/{date}                → resumen de la semana
```

---

## 🚀 Instalación rápida

### Requisitos

- Python 3.10+
- Token de bot de Telegram ([@BotFather](https://t.me/BotFather))

### Pasos

```bash
# 1. Clonar
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora

# 2. Entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac/WSL
# .venv\Scripts\activate   # Windows

# 3. Dependencias
pip install -e .

# 4. Variables de entorno
cp .env.example .env
# Editar .env: añadir TELEGRAM_BOT_TOKEN

# 5. Arrancar
make run-api   # terminal 1 → API en http://localhost:8000
make run-bot   # terminal 2 → Bot Telegram
```

### Variables de entorno

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
THDORA_API_URL=http://localhost:8000   # opcional, por defecto
THDORA_DB_URL=sqlite:///data/thdora.db # opcional, por defecto
```

---

## 🗂️ Estructura del proyecto

```
thdora/
├── src/
│   ├── api/              ← FastAPI: routers, modelos, deps
│   │   └── routers/      ← appointments.py, habits.py, summary.py
│   ├── bot/              ← Bot Telegram: handlers, main, api_client
│   ├── core/             ← Abstracción + implementaciones
│   │   └── impl/         ← SQLiteLifeManager (activo), JsonLifeManager
│   ├── db/               ← SQLAlchemy: base.py, models.py
│   └── ai/               ← (F10 — pendiente)
├── data/                 ← thdora.db (SQLite, no versionado)
├── tests/                ← unit/, integration/, e2e/
├── docs/                 ← Documentación completa
├── pyproject.toml        ← deps: fastapi, sqlalchemy, python-telegram-bot…
└── Makefile              ← make run-api, make run-bot, make test
```

---

## 🛣️ Hoja de ruta

| Fase | Estado | Descripción |
|------|--------|-------------|
| F1–F6 | ✅ | Base, abstracción, API REST, JSON |
| F7 | ✅ | Bot Telegram v2 con inline buttons |
| F8 | ✅ | Endpoints de rango y semana |
| F9 | ✅ | **Persistencia SQLite** |
| F10 | 🔶 | **Gamificación RPG** — XP, niveles, rachas |
| F11 | ⚪ | IA local (Groq / Ollama) |
| F12 | ⚪ | Dashboard web |
| F13 | ⚪ | Despliegue (Docker + VPS) |

---

## 📚 Documentación

- [Índice de documentación](docs/INDEX.md)
- [CHANGELOG](CHANGELOG.md)
- [ROADMAP](ROADMAP.md)
- [Arquitectura](docs/architecture/ARCHITECTURE.md)
- [Módulo DB](docs/modules/db.md)
- [Módulo Bot](docs/modules/bot.md)

---

## 🧪 Tests

```bash
make test
# o directamente:
pytest --cov=src
```

---

## 📄 Licencia

MIT — Álvaro Fernández Mota, 2026
