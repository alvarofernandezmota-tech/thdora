# 📝 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [ROADMAP](ROADMAP.md) · [Arquitectura](docs/architecture/ARCHITECTURE.md)

Todos los cambios importantes del proyecto se documentan aquí.  
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [0.7.0] — 2026-03-27

### Añadido
- `src/bot/api_client.py` — cliente HTTP asíncrono completo con clase `ThdoraApiClient`
  - Métodos: `health`, `get_appointments`, `create_appointment`, `delete_appointment`, `get_habits`, `log_habit`, `get_summary`
  - Manejo de errores con `ApiError`, timeouts configurables, logging
- `src/bot/handlers.py` — handlers completos para todos los comandos del bot
  - `/start`, `/citas`, `/nueva` (ConversationHandler 4 pasos), `/borrar`
  - `/habitos`, `/habito` (ConversationHandler 2 pasos), `/resumen`, `/cancelar`
  - Teclados inline para tipo de cita y hábitos comunes
- `src/bot/main.py` — entrypoint con `load_dotenv()`, comprobación de API al arrancar

### Corregido
- `api_client.py` — rutas adaptadas a la API real:
  - `create_appointment` → `POST /appointments/{date}` (era `POST /appointments`)
  - `log_habit` → `POST /habits/{date}` (era `POST /habits`)
  - `delete_appointment` → `DELETE /appointments/{date}/{index}`
  - `get_habits` → convierte `List[{habit,value}]` a `Dict` automáticamente
- `main.py` — añadido `load_dotenv()` para leer `.env` sin `export` manual

### Estado actual del bot
- ✅ Funciona: `/start`, `/citas`, `/resumen`, `/habitos` (lectura)
- ✅ Funciona: arranque automático con token del `.env`
- ⚠️ Pendiente: flujos `/nueva` y `/habito` — mejorar con:
  - Fechas y horas flexibles con `dateparser`
  - Nombre en el flujo `/nueva` (actualmente falta el paso)
  - Botones inline en `/citas` y `/habitos` para borrar/editar directamente
  - Hábitos acumulables (`+2L` suma al valor existente)
  - Eliminar `/borrar <id>` — reemplazar por botones desde la lista

### Pendiente (Fase 7)
- Reescribir `handlers.py` con flujos mejorados
- Añadir `PUT /appointments/{date}/{index}` y `PUT/DELETE /habits/{date}/{habit}` a los routers
- Instalar `dateparser` y añadir a `pyproject.toml`
- Docker Compose con servicios `api` + `bot`

---

## [0.6.1] — 2026-03-25

### Añadido
- `GET /summary/{date}` — endpoint de resumen diario (citas + hábitos) — **cierra Fase 6**
- `src/api/routers/summary.py` — nuevo router
- `src/api/models/summary.py` — modelo Pydantic `DaySummaryResponse`

### Actualizado
- `src/api/main.py` — versión bumpeada a 0.6.0, registrado router de summary
- `docs/diarios/2026-03-25.md` — diario completo de la sesión (09:00–10:45)

### Pendiente
- Test de integración para `GET /summary/{date}` (inicio Fase 7)

---

## [0.6.0] — 2026-03-25

### Limpieza y reorganización
- Eliminados 8 ficheros zombie de `src/core/` y `src/api/` raíz
- Coverage total subió de 45% a 87%
- Tests reorganizados en `unit/` + `integration/` + `e2e/`
- Eliminados tests duplicados de `tests/` raíz

### Añadido
- Validación de hora y tipo en `MemoryLifeManager.create_appointment()`
- 2 tests nuevos: `test_value_error_hora_invalida`, `test_value_error_tipo_invalido`
- `tests/integration/test_api.py` en su ubicación correcta
- `tests/unit/test_json_lifemanager.py` en su ubicación correcta
- `docs/setup/SETUP.md` — guía de instalación y desarrollo
- `docs/auditoria/2026-03-25.md` — auditoría completa

### Actualizado
- `docs/architecture/ARCHITECTURE.md` — estado real del sistema
- `docs/modules/core.md` — JsonLifeManager documentado como completado
- `docs/modules/api.md` — todos los endpoints reales

### Métricas
- 57/57 tests pasando | Coverage: 87% | `memory_lifemanager`: 100% | `json_lifemanager`: 100%

---

## [0.5.0] — 2026-03-24 (noche)

### Añadido
- `src/core/impl/memory_lifemanager.py`, `src/core/impl/json_lifemanager.py`
- `src/core/interfaces/abstract_lifemanager.py`
- `src/api/routers/appointments.py`, `src/api/routers/habits.py`
- `src/api/models/appointment.py`, `src/api/models/habit.py`
- `src/api/main.py` con dependency injection
- Tests unitarios e integración (61 tests)
- `docs/GIT_GUIDE.md`

### Infraestructura WSL2
- WSL2 en `~/projects/thdora`, git identity y PAT configurados

---

## [0.4.0] — 2026-03-24

### Añadido
- `docs/INDEX.md`, `docs/setup/entorno-local.md`
- `docs/auditoria/thea-ia.md`
- ADR-003 JSON persistence, ADR-004 relación thea-ia

---

## [0.3.0] — 2026-03-24

### Añadido
- ADR-001, ADR-002, `docs/architecture/ARCHITECTURE.md`
- `docs/modules/core.md`, `docs/modules/api.md`
- Diarios 2026-03-23 y 2026-03-24

---

## [0.2.0] — 2026-03-24

### Añadido
- `AbstractLifeManager` ABC, `MemoryLifeManager`, 13 tests unitarios, bot CLI

---

## [0.1.0] — 2026-03-24

### Añadido
- Repo inicial: `pyproject.toml`, `Makefile`, `.gitignore`, estructura base

---

_Última actualización: 27 marzo 2026 — 20:57 CET_
