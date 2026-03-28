# 📝 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [ROADMAP](ROADMAP.md)

Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

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

### Versión handlers
- v3.0 (F9.3) → v3.3 (F9.4) → **v3.4** (F9.5-c2) — archivo único `src/bot/handlers.py`

### ⚠️ Pendiente de prueba en vivo
> F9.3, F9.4 y F9.5 están implementadas y en `main` pero **no han sido probadas en entorno real**.
> La sesión de prueba está programada para la próxima sesión (F9.6 previa).

---

## [0.8.1] — 2026-03-28

### Mantenimiento — Auditoría + Limpieza repo
- Eliminado archivo basura `api_client, handlers y main"` (53KB pegado por error en raíz)
- Eliminado `.env~` (fichero vacío mal versionado)
- `docs/sessions/2026-03-28-session-auditoria.md` — sesión de auditoría documentada
- Verificado estado real del repo: F9.1→F9.4 ✅ completas, F9.5 🔜 Next
- Rama `feat/delete-appointment` identificada como obsoleta (superada por SQLiteLifeManager)

---

## [0.8.0] — 2026-03-27 (noche)

### Añadido — F9: Persistencia SQLite
- `src/db/__init__.py` — módulo de persistencia
- `src/db/base.py` — engine SQLAlchemy, `get_session()`, `init_db()`, `Base` declarativa
- `src/db/models.py` — ORM: tablas `appointments` + `habits` con `to_dict()`
- `src/core/impl/sqlite_lifemanager.py` — `SQLiteLifeManager` completo
- `src/api/deps.py` — singleton `SQLiteLifeManager` vía `lru_cache`
- `data/.gitkeep` — carpeta donde vive `thdora.db`
- `docs/modules/db.md` — documentación completa del módulo DB
- `pyproject.toml` — v0.8.0, `sqlalchemy>=2.0.0` en deps

### Añadido — F9.1: Routers migrados a SQLite
- `src/api/routers/appointments.py` — reescrito completo con SQLite
- `src/api/routers/habits.py` — reescrito completo con SQLite
- `src/api/routers/summary.py` — reescrito con `GET /summary/week/{date}`

### Añadido — F7 fixes (handlers v2.1)
- Fix bug tipo `/nueva`
- Fix contexto acum suelto: `_clean_acum_context()`
- Helper `_skip_to()` y `_skip_to_type()`

---

## [0.7.1] — 2026-03-27

### Añadido
- `src/api/deps.py` — singleton `get_manager()`
- Endpoint `PUT /appointments/{date}/{index}` — editar cita
- Endpoints `DELETE/PUT /habits/{date}/{habit}` — borrar/editar hábito
- `src/bot/api_client.py` — `update_appointment`, `delete_habit`, `update_habit`
- `src/bot/handlers.py` v2: flujo `/nueva` 5 pasos, fechas flexibles, inline buttons, acumulación `+N`

---

## [0.7.0] — 2026-03-27

### Añadido
- `src/bot/api_client.py` — cliente HTTP asíncrono `ThdoraApiClient`
- `src/bot/handlers.py` v1
- `src/bot/main.py` — entrypoint con health check

---

## [0.6.1] — 2026-03-25
### Añadido
- `GET /summary/{date}` — resumen diario (citas + hábitos)

## [0.6.0] — 2026-03-25
### Limpieza
- Eliminados 8 ficheros zombie de `src/core/` y `src/api/` raíz
- Coverage total subió de 45% a 87%
- Tests reorganizados en `unit/` + `integration/` + `e2e/`

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

_Última actualización: 28 marzo 2026 — 22:38 CET_
