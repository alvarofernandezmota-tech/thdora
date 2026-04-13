# CÓMO PROCEDER — THDORA

Guía de trabajo para continuar el desarrollo de forma ordenada.
Actualizado: 2026-04-14.

---

## Estado actual (v4.1.0)

### ✅ Completado y funcionando

| Módulo | Estado | Notas |
|---|---|---|
| `main.py` | ✅ | Scheduler en `post_init`, sin conflicto `quick_config` |
| `handlers/citas.py` | ✅ | Crear, editar (botones), borrar, detalle, recordatorios |
| `handlers/habitos.py` | ✅ | Registrar, editar (botones), borrar, sumar, conflicto |
| `handlers/config.py` | ✅ | Hábitos (CRUD config) + Notificaciones (hora, toggles, offsets) |
| `handlers/menu.py` | ✅ | `/start` programa jobs diarios del scheduler |
| `handlers/common.py` | ✅ | `/resumen`, `/cancelar`, error handler con aviso al usuario |
| `handlers/semana.py` | ✅ | Vista semanal con navegación |
| `keyboards.py` | ✅ | Todos los teclados inline centralizados |
| `scheduler.py` | ✅ | daily_summary, evening_log, apt_reminder sin duplicados |
| `api_client.py` | ✅ | Cliente HTTP para FastAPI |

### 🔔 Warnings conocidos (no son errores)

```
PTBUserWarning: If 'per_message=False', 'CallbackQueryHandler' will not be tracked...
```
Esto es informativo de PTB v22+. No afecta al funcionamiento. Se puede suprimir
añadiendo `per_message=True` a los ConversationHandlers que solo usan
CallbackQueryHandlers, pero requiere validar que los estados no se mezclen
entre mensajes distintos. **Tarea pendiente opcional**.

---

## Reglas de trabajo

### Callbacks con fechas
Los prefijos `ae_`, `ad_`, `adc_` usan `rsplit('_', 1)` para extraer
`(date_str, index)`. Los prefijos `hd_`, `hdc_`, `he_`, `ha_` usan
slice fijo `[:10]` / `[11:]`. **Nunca usar `split('_', 2)` con fechas.**

### Scheduler
- `schedule_user_jobs(bot, user_id, cfg)` es **idempotente**: hace
  `remove_job` antes de `add_job`. Llamar siempre que cambie la hora.
- Los toggles on/off **no reprograman** — solo cambian el campo en la API.
- `schedule_apt_reminders` y `cancel_apt_reminders` se gestionan en `citas.py`.

### ConversationHandlers — rangos de estados

| Handler | Rango |
|---|---|
| `/nueva` (citas) | 0–8 |
| `/habito` | 10–12 |
| editar cita | 20–24 |
| editar hábito | 30–32 |
| `/config` hábitos | 40–44 |
| `/config` notificaciones | 45–47 |
| CFG_DEL_CONF | 48 |

### quick_config
`quick_config` es **entry_point** de `build_config_handler()`. **NO registrar**
como handler global en `main.py` o habrá conflicto de captura.

---

## Próximos pasos sugeridos (por orden de impacto)

### P1 — Tests
- Añadir tests unitarios para `_parse_apt_callback` y `_parse_hab_callback`.
- Tests de integración para los flujos principales con `pytest-asyncio`.
- CI ya está configurado en `.github/workflows/`.

### P2 — Persistencia del scheduler
- Actualmente los jobs se pierden si el bot se reinicia (APScheduler en memoria).
- Migrar a `APScheduler` con `SQLAlchemyJobStore` usando la misma DB de FastAPI.

### P3 — `per_message=True` en ConversationHandlers
- Evaluar cambiar a `per_message=True` en los handlers que solo usan
  `CallbackQueryHandler` para eliminar los PTBUserWarnings.

### P4 — Comando `/ayuda`
- Listar todos los comandos disponibles con descripción breve.

### P5 — Deploy
- Dockerfile y docker-compose ya están listos.
- Configurar variables en `.env` (ver `.env.example`).
- `make docker-up` para arrancar todo en producción.

---

## Arranque rápido

```bash
# Terminal 1 — API
make run-api

# Terminal 2 — Bot
make run-bot

# O todo en tmux
tmux new-session -d -s thdora 'make run-api' \; split-window -h 'sleep 3 && make run-bot' \; attach
```

Después de arrancar, mandar `/start` al bot para programar los jobs diarios.
