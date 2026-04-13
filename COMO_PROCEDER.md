# 🧭 THDORA — Cómo proceder

> Guía de trabajo para retomar el proyecto después de un descanso.
> Estado al día, siguiente paso claro, sin buscar contexto.
>
> **Navegación:** [README](README.md) · [ROADMAP](ROADMAP.md) · [Índice docs](docs/INDEX.md)

---

## 📍 Estado actual — 13 abril 2026

**Versión:** `v0.12.0`

### ✅ Implementado y listo para probar

| Feature | Estado |
|---------|--------|
| CRUD citas + hábitos (SQLite) | ✅ probado en vivo |
| Bot Telegram completo (`/start` `/citas` `/habitos` `/habito` `/nueva` `/semana` `/resumen` `/config` `/cancelar`) | ✅ probado en vivo |
| Franjas horarias en `/nueva` | ✅ probado en vivo |
| `/config → Hábitos` (tipos + botones rápidos) | ✅ probado en vivo |
| **F12 Notificaciones proactivas** (APScheduler) | ✅ implementado, **pendiente probar** |
| **F10 Docker** (`docker compose up -d`) | ✅ listo, **pendiente probar** |

### ❌ Pendiente de implementar
- F11 Multi-usuario
- F13 IA conversacional
- F14 Tracking personal
- F15 Gamificación

---

## ⏭️ Siguiente paso — Probar F12 + F10

No hay nada que implementar. El siguiente paso es **probar** lo que ya está escrito.
Sigue el checklist de abajo.

---

## 🧪 Checklist de pruebas — F12 Notificaciones

### 0. Arrancar (modo local, WSL)

```bash
cd /home/alvaro/projects/thdora
git pull
source .venv/bin/activate
pip install -r requirements.txt   # instala APScheduler si no está

# Terminal 1
make run-api

# Terminal 2
make run-bot
```

En los logs del bot debes ver:
```
✅ API de THDORA disponible en http://localhost:8000
⏰ Scheduler F12 iniciado
🤖 THDORA bot v4.0 arrancando (polling)…
```

Si falta algo:
- `⚠️ API no responde` → revisa que `make run-api` está corriendo
- `ModuleNotFoundError: apscheduler` → `pip install apscheduler`

---

### 1. Comprobar endpoint de config

```bash
# Sustituye TU_ID por tu Telegram user_id
# (¿cómo saberlo? envía /start al bot y mira los logs, o usa @userinfobot)
curl http://localhost:8000/user_config/TU_ID
```

Esperas:
```json
{
  "user_id": "TU_ID",
  "daily_summary_enabled": true,
  "daily_summary_time": "08:00",
  "notif_enabled": true,
  "notif_offsets": ["60", "30", "15"],
  "evening_log_enabled": true,
  "evening_log_time": "22:00"
}
```

---

### 2. Probar /config → Notificaciones en Telegram

1. Escribe `/config` en Telegram
2. Aparece menú con **🧠 Hábitos** y **🔔 Notificaciones**
3. Pulsa **Notificaciones** → verás estado actual con ✅/❌ por cada opción
4. Activa/desactiva **Resumen diario** → el icono cambia al instante
5. Pulsa **⏰ Hora resumen** → elige una hora cercana (2-3 min en el futuro)
6. Pulsa **⏰ Minutos antes de cita** → elige `5 min`
7. Pulsa **← Volver** → vuelves al menú raíz

---

### 3. Probar aviso automático de cita

```
/nueva
→ fecha: hoy
→ franja: la que corresponda ahora
→ hora: 3-5 min en el futuro
→ nombre: Test aviso
→ tipo: personal
→ /skip notas
```

Espera X minutos → debes recibir:
```
🔔 Recordatorio
En 5 min tienes:
  ⏰ HH:MM — Test aviso
```

---

### 4. Probar cancel al borrar

- Ve a `/citas hoy` → borra la cita • el aviso debe cancelarse (no llega)

---

### 5. Probar resumen diario

- Ve a **Notificaciones** → pon hora del resumen 2 min en el futuro → espera
- Debes recibir mensaje con las citas del día

---

### 6. Probar Docker (opcional, si quieres)

```bash
cd /home/alvaro/projects/thdora
cp docker/.env.docker.example .env   # solo primera vez
# editar .env y poner TELEGRAM_BOT_TOKEN=...

make docker-build
make docker-up
make docker-logs     # ver que arranca bien
make docker-down     # parar cuando termines
```

Si ves los mismos logs que en local → Docker funciona. Bot listo para 24/7.

---

## 🛠️ Referencia rápida de comandos

```bash
# Local
make run-api          # API en http://localhost:8000
make run-bot          # Bot Telegram

# Docker
make docker-build     # construir imagen
make docker-up        # arrancar en segundo plano
make docker-down      # parar
make docker-logs      # ver logs en vivo
make docker-logs-api  # solo API
make docker-logs-bot  # solo bot
make docker-restart   # reiniciar sin reconstruir
make docker-rebuild   # rebuild completo desde cero
make docker-db        # consola SQLite dentro del contenedor

# Tests
make test             # todos
make test-bot         # solo bot
make test-cov         # con cobertura HTML
```

---

## 📁 Estructura completa del proyecto

```
thdora/
├── src/
│   ├── core/
│   │   ├── abstract/          ← AbstractLifeManager
│   │   └── impl/              ← SQLiteLifeManager
│   ├── db/
│   │   ├── models.py          ← Appointment, Habit, HabitConfig, UserConfig [F12]
│   │   └── base.py
│   ├── api/
│   │   ├── main.py            ← FastAPI v0.12.0
│   │   └── routers/
│   │       ├── appointments.py
│   │       ├── habits.py
│   │       ├── habit_config.py
│   │       ├── summary.py
│   │       └── user_config.py     ← GET + PUT /user_config/{user_id} [F12]
│   └── bot/
│       ├── main.py            ← v4.0 + arranca scheduler [F12]
│       ├── api_client.py      ← + get/update_user_config [F12]
│       ├── keyboards.py       ← + _kb_config_menu, _kb_notif_* [F12]
│       ├── scheduler.py       ← APScheduler jobs [F12 ★ nuevo]
│       ├── utils/
│       │   ├── dates.py
│       │   └── accum.py
│       └── handlers/
│           ├── menu.py
│           ├── citas.py           ← + hooks scheduler [F12]
│           ├── habitos.py
│           ├── semana.py
│           ├── config.py          ← menú raíz + Notificaciones [F12]
│           └── common.py
├── data/
│   └── thdora.db              ← SQLite (no versionado)
├── docker/
│   ├── entrypoint-api.sh
│   ├── entrypoint-bot.sh
│   └── .env.docker.example    ← copiar a .env para Docker
├── docs/                  ← arquitectura, ADRs, flujos, API reference
├── tests/
├── Dockerfile
├── docker-compose.yml
├── COMO_PROCEDER.md       ← ⭐ empieza aquí cada sesión
├── README.md
├── ROADMAP.md
├── CHANGELOG.md
├── requirements.txt       ← incluye APScheduler [F10]
├── pyproject.toml
├── Makefile
└── .env.example
```

---

## 📖 Documentación disponible

| Doc | Para qué sirve |
|-----|----------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Estructura y decisiones de diseño |
| [docs/FLUJOS_DETALLADOS.md](docs/FLUJOS_DETALLADOS.md) | Estados, transiciones, casos borde de todos los flujos |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | Todos los endpoints con ejemplos |
| [docs/CONVENCIONES.md](docs/CONVENCIONES.md) | Patrones callback_data, convenciones de código |
| [docs/F12_NOTIFICACIONES_DESIGN.md](docs/F12_NOTIFICACIONES_DESIGN.md) | Diseño completo de F12 |
| [docs/INDEX.md](docs/INDEX.md) | Mapa completo de toda la documentación |

---

## 📅 Convenciones callback_data

```
ad_  adc_        → borrar / confirmar cita
ae_              → editar cita
hd_  hdc_        → borrar / confirmar hábito
he_              → editar hábito
ha_              → sumar a hábito
hval_            → valor rápido hábito
hconf_           → resolver conflicto hábito
cfg_             → config menú raíz
notif_           → acciones notificaciones
cfgt_            → tipo de hábito en config
# Lista completa → docs/CONVENCIONES.md
```

---

_Última actualización: 13 abril 2026 — 22:45 CEST_
