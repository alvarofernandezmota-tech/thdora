# 📝 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [ROADMAP](ROADMAP.md) · [Arquitectura](docs/architecture/ARCHITECTURE.md)

Todos los cambios importantes del proyecto se documentan aquí.  
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [0.6.0] — 2026-03-25

### Limpieza y reorganización
- Eliminados 8 ficheros zombie de `src/core/` y `src/api/` raíz (copias antiguas de versiones previas)
- Coverage total subió de 45% a 87% tras la limpieza
- Tests reorganizados en estructura `unit/` + `integration/` + `e2e/`
- Eliminados tests duplicados de `tests/` raíz

### Añadido
- Validación de hora y tipo en `MemoryLifeManager.create_appointment()` (paridad con `JsonLifeManager`)
- 2 tests nuevos en `test_memory_lifemanager.py`: `test_value_error_hora_invalida`, `test_value_error_tipo_invalido`
- `tests/integration/test_api.py` — tests de API en su ubicación correcta
- `tests/unit/test_json_lifemanager.py` — tests de JsonLifeManager en su ubicación correcta
- `docs/setup/SETUP.md` — guía de instalación y desarrollo
- `docs/auditoria/2026-03-25.md` — auditoría completa del repositorio

### Actualizado
- `docs/architecture/ARCHITECTURE.md` — estado real del sistema (diagrama, estructura, módulos, fases, coverage)
- `docs/modules/core.md` — JsonLifeManager documentado como completado
- `docs/modules/api.md` — todos los endpoints reales con body, códigos de estado y errores

### Métricas
- Tests: 57/57 pasando (0 fallando)
- Coverage: 87% total
- `memory_lifemanager`: 100%
- `json_lifemanager`: 100%
- `routers/appointments`: 100%
- `routers/habits`: 100%

---

## [0.5.0] — 2026-03-24 (noche)

### Añadido
- `src/core/impl/memory_lifemanager.py` — implementación en memoria
- `src/core/impl/json_lifemanager.py` — implementación con persistencia JSON
- `src/core/interfaces/abstract_lifemanager.py` — interfaz abstracta ABC
- `src/api/routers/appointments.py` — router FastAPI para citas
- `src/api/routers/habits.py` — router FastAPI para hábitos
- `src/api/models/appointment.py` — modelos Pydantic de citas
- `src/api/models/habit.py` — modelos Pydantic de hábitos
- `src/api/main.py` — entry point FastAPI con dependency injection
- Tests unitarios e integración (61 tests)
- `docs/GIT_GUIDE.md` — guía de flujo Git

### Infraestructura WSL2 (resuelto en esta sesión)
- WSL2 clonado correctamente en `~/projects/thdora`
- Git identity configurada: `alvarofernandezmota-tech`
- Credenciales GitHub con PAT configurado

---

## [0.4.0] — 2026-03-24

### Añadido
- `docs/INDEX.md` — índice maestro de documentación
- `docs/setup/entorno-local.md` — guía WSL2 + OpenClaw + Ollama + CUDA + Telegram
- `docs/auditoria/thea-ia.md` — inventario thea-ia y plan de reutilización por fases
- ADR-003 — JSON como primera capa de persistencia
- ADR-004 — Relación thdora/thea-ia
- Sección hardware en setup: GTX 1060, tabla modelos por VRAM

### Actualizado
- `README.md`, `ROADMAP.md` — navegación rápida, estado real

---

## [0.3.0] — 2026-03-24

### Añadido
- ADR-001 — Por qué monorepo
- ADR-002 — Por qué interfaces ABC
- `docs/architecture/ARCHITECTURE.md`
- `docs/modules/core.md`, `docs/modules/api.md`
- Diarios 2026-03-23 y 2026-03-24

---

## [0.2.0] — 2026-03-24

### Añadido
- `AbstractLifeManager` — interfaz ABC
- `MemoryLifeManager` — implementación completa en memoria
- 13 tests unitarios passing
- Bot CLI interactivo

---

## [0.1.0] — 2026-03-24

### Añadido
- Repo creado: estructura enterprise inicial
- `pyproject.toml`, `Makefile`, `.gitignore`
- Estructura `src/`, `tests/`, `docs/`, `datos/`, `docker/`

---

_Última actualización: 25 marzo 2026 — 10:21 CET_
