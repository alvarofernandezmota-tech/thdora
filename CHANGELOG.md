# 📝 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [ROADMAP](ROADMAP.md)

Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [0.8.1] — 2026-03-28

### Mantenimiento — Auditoría + Limpieza repo
- Eliminado archivo basura `api_client, handlers y main"` (53KB pegado por error en raíz)
- Eliminado `.env~` (fichero vacío mal versionado)
- `docs/sessions/2026-03-28-session-auditoria.md` — sesión de auditoría documentada
- Verificado estado real del repo: F9.1→F9.4 ✅ completas, F9.5 🔜 Next
- Rama `feat/delete-appointment` identificada como obsoleta (superada por SQLiteLifeManager)

### Estado verificado
- `src/bot/handlers.py` v2.1 — 60KB, operativo
- `src/bot/api_client.py` — 10KB, operativo
- `src/db/` + `SQLiteLifeManager` — F9 completa y en producción
- `src/api/` routers migrados — todos usando SQLite
- `docs/PERSONAL-DATA-PLATFORM.md` — roadmap alineado con estado real

---

## [0.8.0] — 2026-03-27 (noche)

### Añadido — F9: Persistencia SQLite
- `src/db/__init__.py` — módulo de persistencia
- `src/db/base.py` — engine SQLAlchemy, `get_session()`, `init_db()`, `Base` declarativa
- `src/db/models.py` — ORM: tablas `appointments` + `habits` con `to_dict()`
- `src/db/migrations/README.md` — Alembic pendiente F9.2
- `src/core/impl/sqlite_lifemanager.py` — `SQLiteLifeManager` completo:
  - CRUD citas: `get/create/delete/update_appointment`
  - CRUD hábitos: `get/log/delete/update_habit` con upsert
  - Extras: `get_appointments_range`, `get_upcoming_appointments`, `get_habits_range`, `get_summary`
- `src/api/deps.py` — reescrito: singleton `SQLiteLifeManager` vía `lru_cache`
- `data/.gitkeep` — carpeta donde vive `thdora.db`
- `docs/modules/db.md` — documentación completa del módulo DB
- `pyproject.toml` — v0.8.0, `sqlalchemy>=2.0.0` en deps, `alembic` en dev

### Añadido — F9.1: Routers migrados a SQLite
- `src/api/routers/appointments.py` — **reescrito completo**:
  - Usa `SQLiteLifeManager` (abandona `JsonLifeManager`)
  - Nuevos endpoints: `GET /appointments/week/{date}`, `GET /appointments/range/{from}/{to}`, `GET /appointments/upcoming/{date}?limit=N`
- `src/api/routers/habits.py` — **reescrito completo**:
  - Usa `SQLiteLifeManager`
  - Nuevos endpoints: `GET /habits/week/{date}`, `GET /habits/range/{from}/{to}`, `GET /habits/stats/{habit}?days=N`
- `src/api/routers/summary.py` — reescrito: nuevo `GET /summary/week/{date}`

### Añadido — F7 fixes (handlers v2.1)
- `src/bot/handlers.py` v2.1:
  - Fix bug tipo `/nueva`: `etipo_` y `tipo_` son patrones distintos — ya no se interfieren
  - Fix contexto acum suelto: `_clean_acum_context()` al entrar en `/citas` y `/habitos`
  - `_clean_acum_context()` también al completar la acumulación
  - Helper `_skip_to()` y `_skip_to_type()` para flujo edición limpio

### Cambios de arquitectura
- `JsonLifeManager` sigue disponible pero ya no se usa en producción
- Los datos ahora viven en `data/thdora.db` (SQLite), persisten entre reinicios
- `data/` añadido a `.gitignore` (no versionar la BD)

---

## [0.7.1] — 2026-03-27

### Añadido
- `src/api/deps.py` — singleton `get_manager()` con `lru_cache(maxsize=1)`
- Endpoint `PUT /appointments/{date}/{index}` — editar cita
- Endpoints `DELETE/PUT /habits/{date}/{habit}` — borrar/editar hábito
- `src/bot/api_client.py` — métodos: `update_appointment`, `delete_habit`, `update_habit`, `_put()`
- `src/bot/handlers.py` v2: flujo `/nueva` 5 pasos, fechas flexibles, inline buttons, acumulación `+N`
- `docs/modules/bot.md` — documentación completa del módulo bot

---

## [0.7.0] — 2026-03-27

### Añadido
- `src/bot/api_client.py` — cliente HTTP asíncrono con `ThdoraApiClient`
- `src/bot/handlers.py` v1
- `src/bot/main.py` — entrypoint con health check

---

## [0.6.1] — 2026-03-25

### Añadido
- `GET /summary/{date}` — resumen diario (citas + hábitos)

---

## [0.6.0] — 2026-03-25

### Limpieza
- Eliminados 8 ficheros zombie de `src/core/` y `src/api/` raíz
- Coverage total subió de 45% a 87%
- Tests reorganizados en `unit/` + `integration/` + `e2e/`

---

## [0.5.0] — 2026-03-24 (noche)

### Añadido
- `MemoryLifeManager`, `JsonLifeManager`
- Routers `appointments.py`, `habits.py`
- 61 tests unitarios + integración

---

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

_Última actualización: 28 marzo 2026 — 16:25 CET_
