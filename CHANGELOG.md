# 📝 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [ROADMAP](ROADMAP.md)

Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [0.10.0] — 2026-04-12

### Refactor — F9.6: handlers.py monolítico → módulos (✅ completado)

**`src/bot/handlers.py` (60KB, ~1500 líneas) eliminado y dividido en:**

| Módulo | Contenido |
|--------|----------|
| `src/bot/utils/dates.py` | `_parse_date_flex`, `_parse_date_arg`, `_date_label`, `_date_short`, `_greeting`, `_monday` |
| `src/bot/utils/accum.py` | `_accumulate_value`, `_clean_acum_context` |
| `src/bot/keyboards.py` | Todos los `_kb_*`, `_nav_keyboard`, constantes `TIPOS_CITA`, `FRANJAS`, `HABIT_TYPE_EMOJIS` |
| `src/bot/handlers/menu.py` | `cmd_start`, `cb_menu_home`, `cb_quick_dispatch` |
| `src/bot/handlers/citas.py` | `cmd_citas`, nav, detail, borrar/editar, `/nueva` + **FRANJAS HORARIAS** |
| `src/bot/handlers/habitos.py` | `cmd_habitos`, nav, `/habito`, borrar/editar/sumar |
| `src/bot/handlers/semana.py` | `cmd_semana`, `cb_semana_nav` |
| `src/bot/handlers/config.py` | `cmd_config`, `build_config_handler` |
| `src/bot/handlers/common.py` | `cmd_cancelar`, `cb_cancel_action`, `cmd_resumen`, `error_handler` |
| `src/bot/handlers/__init__.py` | Re-exporta todo — `main.py` sin cambios |

### Añadido — F9.5 (pendiente): Franjas horarias en /nueva (✅ implementado)

Flujo `/nueva` rediseñado con selección progresiva de hora:

```
Paso 1 → Fecha (texto libre: hoy, mañana, 27/03…)
Paso 2 → Franja: [🌅 Mañana 6-14] [🌆 Tarde 14-22] [🌙 Noche 22-6] [✏️ Exacta]
Paso 3 → Hora en punto: botones [06:00][07:00]…[13:00] + [🕐 Ver cuartos][✏️ Exacta]
Paso 4 → Cuartos (opcional): [HH:00][HH:15][HH:30][HH:45] + [✏️ Exacta]
Paso 5 → Nombre (texto libre)
Paso 6 → Tipo [Médica][Personal][Trabajo][Otra]
Paso 7 → Notas o /skip
```

Estados nuevos en `ConversationHandler`:
- `NUEVA_FRANJA` — elección de franja con botones
- `NUEVA_HORA_PUNTO` — hora en punto de la franja
- `NUEVA_HORA_CUARTO` — cuartos opcionales
- `NUEVA_TIME` — escritura manual HH:MM (siempre disponible)
- Al cambiar hora por conflicto → vuelve a `NUEVA_FRANJA` (no a texto libre)

### main.py
- Sin cambios — los imports siguen funcionando igual vía `src.bot.handlers.__init__`

---

## [0.9.0] — 2026-03-28

### Añadido — F9.5: UX avanzada bot (handlers v3.4)
- **Saludo contextual** según hora: 🌅 Buenos días / 🌆 Buenas tardes / 🌙 Buenas noches
- **Fecha real visible** en botón central de navegación: `[Sáb 28 mar]`
- **➕ Nueva cita** directo desde vista `/citas` del día (sin pasar por menú)
- **➕ Nuevo hábito** directo desde vista `/habitos` del día
- **Nombre de hábito libre** — eliminados `HABITOS_COMUNES` hardcodeados
- **Editar nombre del hábito** además del valor (nuevo estado `EDIT_HAB_NOMBRE`)
- Flujo `/habito`: fecha prefijada → nombre libre → valor
- Confirmación visual con resumen al crear/editar cita o hábito
- Fix bug semana: lunes mal calculado en `_monday()`

### Añadido — F9.4: Vista detalle de cita
- Click en ⏰ hora de la cita → vista detalle completa
- Vista detalle muestra: fecha, hora, nombre, tipo, notas
- Botones Editar / Borrar / ← Volver directamente desde vista detalle
- `cb_cita_detail` registrado en `main.py`

### Añadido — F9.3: UI unificada
- Menú principal `/start` con botones inline
- Navegación ◀️▶️ en vistas `/citas` y `/habitos`
- Botón 🏠 Menú desde todas las vistas
- Botón ← Volver al día desde cualquier acción
- Cambio de vista Citas ↔ Hábitos desde la barra de navegación
- Botón 📋 Semana desde citas y hábitos

### ⚠️ Pendiente de prueba en vivo
> F9.3, F9.4 y F9.5 están implementadas en `main` pero **no han sido probadas en entorno real**.
> Primera prueba prevista para la próxima sesión presencial.

---

## [0.8.1] — 2026-03-28

### Mantenimiento — Auditoría + Limpieza repo
- Eliminado archivo basura `api_client, handlers y main"` (53KB pegado por error en raíz)
- Eliminado `.env~` (fichero vacío mal versionado)
- `docs/sessions/2026-03-28-session-auditoria.md` — sesión de auditoría documentada
- Verificado estado real del repo: F9.1→F9.4 ✅ completas, F9.5 🔜 Next
- Rama `feat/delete-appointment` identificada como obsoleta

---

## [0.8.0] — 2026-03-27 (noche)

### Añadido — F9: Persistencia SQLite
- `src/db/__init__.py` — módulo de persistencia
- `src/db/base.py` — engine SQLAlchemy, `get_session()`, `init_db()`, `Base` declarativa
- `src/db/models.py` — ORM: tablas `appointments` + `habits` con `to_dict()`
- `src/core/impl/sqlite_lifemanager.py` — `SQLiteLifeManager` completo
- `src/api/deps.py` — singleton `SQLiteLifeManager` vía `lru_cache`
- `data/.gitkeep` — carpeta donde vive `thdora.db`

### Añadido — F9.1: Routers migrados a SQLite
- `src/api/routers/appointments.py` — reescrito completo con SQLite
- `src/api/routers/habits.py` — reescrito completo con SQLite
- `src/api/routers/summary.py` — reescrito con `GET /summary/week/{date}`

---

## [0.7.1] — 2026-03-27
### Añadido
- Endpoint `PUT /appointments/{date}/{index}` — editar cita
- Endpoints `DELETE/PUT /habits/{date}/{habit}` — borrar/editar hábito
- `src/bot/handlers.py` v2: flujo `/nueva` 5 pasos, fechas flexibles, inline buttons

## [0.7.0] — 2026-03-27
### Añadido
- `src/bot/api_client.py` — cliente HTTP asíncrono `ThdoraApiClient`
- `src/bot/handlers.py` v1
- `src/bot/main.py` — entrypoint con health check

## [0.6.1] — 2026-03-25
### Añadido
- `GET /summary/{date}` — resumen diario (citas + hábitos)

## [0.6.0] — 2026-03-25
### Limpieza
- Eliminados 8 ficheros zombie de `src/core/` y `src/api/` raíz
- Coverage total subió de 45% a 87%

## [0.5.0] — 2026-03-24 (noche)
### Añadido
- `MemoryLifeManager`, `JsonLifeManager`
- Routers `appointments.py`, `habits.py`
- 61 tests unitarios + integración

## [0.4.0] — 2026-03-24
### Añadido
- `docs/INDEX.md`, ADR-003, ADR-004

## [0.3.0] — 2026-03-24
### Añadido
- ADR-001, ADR-002, arquitectura, módulos core y api

## [0.2.0] — 2026-03-24
### Añadido
- `AbstractLifeManager`, `MemoryLifeManager`, 13 tests

## [0.1.0] — 2026-03-24
### Añadido
- Repo inicial: estructura base, `pyproject.toml`, `Makefile`

---

_Última actualización: 12 abril 2026 — 21:04 CEST_
