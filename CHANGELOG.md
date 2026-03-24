# CHANGELOG

Todos los cambios notables de este proyecto se documentan en este archivo.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [0.4.0] — 2026-03-24

### Añadido
- Migración completa desde `AppointmentManager` + `personal/thdora` a monorepo
- Estructura enterprise completa: `src/core/`, `src/api/`, `src/bot/`, `src/ai/`
- Documentación exhaustiva de interfaces y módulos
- `AbstractLifeManager` — interfaz ABC integrada en `src/core/interfaces/`
- `MemoryLifeManager` — implementación migrada a `src/core/impl/`
- `docs/architecture/`, `docs/modules/`, `docs/diarios/`
- `pyproject.toml`, `Makefile`, `.github/workflows/`

---

## [0.3.0] — 2026-02-09

### Añadido
- Arquitectura modular 3 capas (data / logic / presentation)
- Estructura docs profesional
- Inicio persistencia JSON (25%)

---

## [0.2.0] — 2026-02-08

### Añadido
- Bot CLI interactivo con menú de 5 opciones
- Refactorización a módulos separados

---

## [0.1.0] — 2026-02-05

### Añadido
- CRUD completo en memoria
- Funciones `agregar_cita`, `ver_citas`, `buscar_cita`, `eliminar_cita`
