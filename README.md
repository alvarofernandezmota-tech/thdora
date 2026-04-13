# THDORA — Tu Asistente Personal de Gestión de Vida

Bot de Telegram + API REST para gestionar citas, hábitos, recordatorios
y notificaciones diarias. Construido con Python, FastAPI y
python-telegram-bot v22.

---

## Arquitectura

```
thdora/
├── src/
│   ├── api/                  # FastAPI — endpoints REST
│   │   ├── routers/          # appointments, habits, config, user_config
│   │   └── models/           # modelos Pydantic + SQLAlchemy
│   └── bot/                  # Bot Telegram
│       ├── main.py           # Entrypoint, registro de handlers, post_init
│       ├── api_client.py     # Cliente HTTP para la FastAPI
│       ├── scheduler.py      # APScheduler: daily_summary, evening_log, apt_reminder
│       ├── keyboards.py      # Todos los teclados inline centralizados
│       ├── handlers/
│       │   ├── __init__.py   # Exports públicos
│       │   ├── citas.py      # /nueva, /citas, editar, borrar, detalle
│       │   ├── habitos.py    # /habito, /habitos, editar, borrar, sumar
│       │   ├── config.py     # /config: hábitos (CRUD) + notificaciones
│       │   ├── menu.py       # /start, 🏠 Menú
│       │   ├── semana.py     # /semana
│       │   └── common.py     # /cancelar, /resumen, error_handler
│       └── utils/
│           ├── dates.py      # Parseo y formato de fechas
│           └── accum.py      # Acumulación de valores de hábitos
├── tests/                    # pytest + pytest-asyncio
├── docs/                     # Documentación técnica extendida
├── README.md
├── CHANGELOG.md
├── ROADMAP.md
├── COMO_PROCEDER.md          # Guía de trabajo incremental
├── Makefile
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Requisitos

- Python 3.10+
- FastAPI + Uvicorn
- python-telegram-bot v22.7
- APScheduler 3.x
- SQLAlchemy 2.x

```bash
pip install -r requirements.txt
```

---

## Configuración

Copiar `.env.example` a `.env` y rellenar:

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
THDORA_API_URL=http://localhost:8000
```

---

## Arranque

```bash
# API (FastAPI)
make run-api

# Bot Telegram
make run-bot

# Docker (producción)
make docker-up
```

Tras arrancar, manda `/start` al bot para programar los jobs diarios
(resumen + evening log).

---

## Comandos del bot

| Comando | Descripción |
|---|---|
| `/start` | Menú principal + programar jobs diarios |
| `/citas` | Ver citas de hoy |
| `/nueva` | Crear nueva cita (flujo con franjas horarias) |
| `/habitos` | Ver hábitos de hoy |
| `/habito` | Registrar un hábito |
| `/semana` | Vista semanal de citas y hábitos |
| `/resumen` | Resumen del día (citas + hábitos) |
| `/config` | Configurar tipos de hábitos y notificaciones |
| `/cancelar` | Cancelar cualquier flujo activo |

---

## Flujos principales

### Nueva cita (`/nueva`)
1. Fecha (texto libre: `hoy`, `mañana`, `27/04`…)
2. Franja: 🌅 Mañana / 🌆 Tarde / 🌙 Noche / ✏️ Exacta
3. Hora (botones de la franja o texto HH:MM)
4. Nombre
5. Tipo (médica / personal / trabajo / otra)
6. Notas o skip

### Editar cita (botón ✏️)
1. Muestra datos actuales
2. Botones: Hora / Nombre / Tipo / Notas
3. Edita solo el campo elegido

### Registro de hábito (`/habito`)
1. Nombre del hábito
2. Valor (botones rápidos si hay config, o texto libre)
3. Si ya existe hoy: Sobreescribir / Sumar / Cancelar

### Configuración (`/config`)
- **Hábitos**: ver configurados, añadir nuevo (tipo + unidad + botones rápidos), borrar
- **Notificaciones**: toggles on/off, hora de resumen diario, hora de evening log,
  minutos antes de cita (5/15/30/60 min o combinaciones)

---

## Scheduler (F12)

- **`daily_summary`**: envía resumen diario (citas + hábitos) a la hora configurada
- **`evening_log`**: recordatorio vespertino para registrar hábitos
- **`apt_reminder`**: avisos one-shot antes de cada cita (según offsets configurados)

Los jobs se programan en `/start` y se reprograman automáticamente al cambiar
la hora en `/config → Notificaciones`.

---

## Tests

```bash
make test
# o
pytest tests/ -v
```

---

## Versión actual

**v4.1.0** — 2026-04-14

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo.
Ver [ROADMAP.md](ROADMAP.md) para próximas funcionalidades.
Ver [COMO_PROCEDER.md](COMO_PROCEDER.md) para guía de trabajo.
