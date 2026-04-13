# CÓMO PROCEDER — THDORA

Guía de trabajo para continuar el desarrollo de forma ordenada.
Actualizado: 2026-04-14.

---

## 🔴 PENDIENTE — Probar antes de tagear v4.1.0

> Estos cambios se hicieron el 2026-04-14 pero **no se han probado en local**.
> Mañana arranca con `git pull && make run-bot` y valida los 3 casos.

### Checklist de pruebas

- [ ] **1. Cancelar en pantalla de horas**
  - `/config` → Notificaciones → ⏰ Hora resumen → pulsa **❌ Cancelar**
  - ✅ Esperado: vuelve al menú de notificaciones sin cambiar nada
  - ✅ Mismo test con ⏰ Hora evening log → ❌ Cancelar

- [ ] **2. Jobs no duplicados al cambiar hora**
  - Cambia la hora del resumen 2 veces seguidas
  - ✅ Esperado: en logs aparece **una sola línea** `daily_summary_XXX programado a las XX:00` cada vez
  - ❌ Si aparece dos veces → hay regresión en `scheduler.py`

- [ ] **3. Borrar config de hábito**
  - `/config` → Hábitos → pulsa 🗑️ Borrar en uno → confirmar
  - ✅ Esperado: mensaje `Config de X eliminada`

- [ ] **4. Skip en config de hábito**
  - `/config` → Hábitos → nuevo hábito → en "unidad" escribe `skip` (sin barra)
  - ✅ Esperado: pasa al paso de botones rápidos sin error

- [ ] **5. Flujo editar cita completo**
  - Crear cita → botón ✏️ → cambiar hora → verificar que el reminder se reprograma en logs
  - Crear cita → botón ✏️ → cambiar nombre → verificar que se actualiza

- [ ] **6. Flujo editar hábito completo**
  - Registrar hábito → botón ✏️ → cambiar valor → verificar que se actualiza
  - Registrar hábito → botón ✏️ → cambiar nombre → verificar que el antiguo desaparece

Una vez validados todos → `git tag v4.1.0 && git push --tags`

---

## Estado actual (v4.1.0 — pendiente validación)

### ✅ Completado (en código)

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
Informativo de PTB v22+. No afecta al funcionamiento. **Tarea pendiente opcional** (ver P3).

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

## Próximos pasos (por orden de impacto)

### P1 — Validar checklist de pruebas (ver arriba)
Antes de cualquier otra cosa.

### P2 — Tests
- Añadir tests unitarios para `_parse_apt_callback` y `_parse_hab_callback`.
- Tests de integración para los flujos principales con `pytest-asyncio`.
- CI ya está configurado en `.github/workflows/`.

### P3 — Persistencia del scheduler
- Actualmente los jobs se pierden si el bot se reinicia (APScheduler en memoria).
- Migrar a `APScheduler` con `SQLAlchemyJobStore` usando la misma DB de FastAPI.

### P4 — `per_message=True` en ConversationHandlers
- Evaluar para eliminar los PTBUserWarnings.

### P5 — Comando `/ayuda`
- Listar todos los comandos disponibles con descripción breve.

### P6 — Deploy
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
