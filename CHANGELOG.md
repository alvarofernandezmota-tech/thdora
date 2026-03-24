# 📝 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [ROADMAP](ROADMAP.md) · [Arquitectura](docs/architecture/ARCHITECTURE.md)

Todos los cambios importantes del proyecto se documentan aquí.  
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [0.5.0] — 2026-03-24 (noche)

### Añadido
- `src/core/abstract_lifemanager.py` — clase base abstracta del LifeManager (subida desde ZIP Claude)
- `src/core/memory_lifemanager.py` — implementación en memoria completa
- `src/core/json_lifemanager.py` — implementación con persistencia JSON
- `src/core/appointment.py` — modelo de dominio Appointment
- `src/core/habit.py` — modelo de dominio Habit
- `src/core/__init__impl.py` — registro de implementaciones disponibles
- `src/api/appointments_router.py` — router FastAPI para citas
- `src/api/habits_router.py` — router FastAPI para hábitos
- `src/api/main.py` — entry point FastAPI actualizado con los nuevos routers
- `tests/test_api.py` — tests de integración de la API
- `tests/test_memory_lifemanager.py` — tests unitarios MemoryLifeManager
- `tests/test_json_lifemanager.py` — tests unitarios JsonLifeManager
- `docs/GIT_GUIDE.md` — guía de flujo Git para el proyecto

### Infraestructura WSL2 (resuelto esta sesión)
- WSL2 clonado correctamente en `~/projects/thdora`
- Git identity configurada: `alvarofernandezmota-tech` / `alvarofernandezmota@gmail.com`
- `unzip` instalado (`sudo apt install unzip`)
- Credenciales GitHub guardadas con `credential.helper store` (PAT configurado)
- Usuario Windows en WSL: `/mnt/c/Users/alvar/`

### Contexto del día
- Archivos generados por Claude (tareas 1-4) entregados como ZIP (`files.zip`)
- Extraídos y organizados manualmente en las rutas correctas del repo
- Push exitoso tras resolver conflicto con `git pull --rebase`
- 13 archivos, 1709 líneas de código nuevas en un solo commit

---

## 🗓️ PRÓXIMA SESIÓN — Checklist

### Antes de escribir código
- [ ] `cd ~/projects/thdora && git pull origin main`
- [ ] `pip install -e .` — instalar dependencias
- [ ] `pytest tests/ -v` — verificar que los tests pasan

### Limpieza y organización
- [ ] Revisar `src/core/__init__impl.py` — nombre raro, posiblemente renombrar a `factory.py`
- [ ] Verificar herencia: `AbstractLifeManager` → `MemoryLifeManager` → `JsonLifeManager`
- [ ] Comprobar imports en `appointments_router.py` y `habits_router.py`
- [ ] Eliminar `.gitkeep` de carpetas que ya tienen contenido

### Desarrollo pendiente
- [ ] `src/ai/` — vacío, pendiente capa de IA (integración Ollama/qwen2.5-coder)
- [ ] `src/bot/` — vacío, pendiente bot Telegram
- [ ] `.env.example` — variables de entorno documentadas
- [ ] GitHub Actions CI — ejecutar pytest automáticamente en cada PR
- [ ] Docker — verificar que `docker-compose up` levanta correctamente

### Documentación
- [ ] Actualizar `README.md` con estado real (qué funciona, qué no)
- [ ] Crear `docs/diarios/2026-03-24-noche.md` con el detalle técnico de esta sesión

---

## [0.4.0] — 2026-03-24

### Añadido
- `docs/INDEX.md` — índice maestro de toda la documentación con navegación completa
- `docs/setup/entorno-local.md` — guía completa WSL2 + OpenClaw + Ollama + CUDA + Telegram
- `docs/auditoria/thea-ia.md` — inventario completo de thea-ia y plan de reutilización por fases
- `ADR-003` — JSON como primera capa de persistencia ([ver](docs/architecture/decisions/ADR-003-json-persistence.md))
- `ADR-004` — Relación thdora/thea-ia: thdora independiente, thea-ia como referencia ([ver](docs/architecture/decisions/ADR-004-relacion-thea-ia.md))
- Sección hardware en setup: GTX 1060, tabla modelos por VRAM, rendimiento CPU vs GPU
- Navegación rápida en README, ROADMAP y CHANGELOG
- Mapa del ecosistema completo en README e INDEX

### Actualizado
- `README.md` — badges corregidos (qwen2.5-coder:7b), tabla navegación rápida, estado real
- `ROADMAP.md` — Fase 4 al 95%, modelo correcto, Fase 8 con CUDA, Fases 9-11 definidas
- `docs/auditoria/thea-ia.md` — añadido contexto histórico y emocional del proyecto

### Contexto del día
- Auditoría completa de thea-ia: descubierto NLP engine (15KB), orquestador (14KB), router (14KB), callbacks (17KB), conversation manager (10KB), sistema multi-agente, BD real
- Decisión: thea-ia es el proyecto original con meses de trabajo real — no se borra, no se archiva
- thdora es la evolución consciente de thea-ia, no un reemplazo

---

## [0.3.0] — 2026-03-24

### Añadido
- `ADR-001` — Por qué monorepo ([ver](docs/architecture/decisions/ADR-001-monorepo.md))
- `ADR-002` — Por qué interfaces ABC ([ver](docs/architecture/decisions/ADR-002-abc-interfaces.md))
- `docs/architecture/ARCHITECTURE.md` — arquitectura completa del sistema
- `docs/modules/core.md` — documentación del módulo core
- `docs/modules/api.md` — documentación del módulo API
- `docs/diarios/2026-03-23.md` — setup OpenClaw + Ollama + primera conversación Telegram
- `docs/diarios/2026-03-24.md` — nacimiento repo thdora, arquitectura, interfaces

---

## [0.2.0] — 2026-03-24

### Añadido
- `AbstractLifeManager` — interfaz ABC con métodos abstractos para citas y hábitos
- `MemoryLifeManager` — implementación completa en memoria
- 13 tests unitarios passing (pytest)
- Bot CLI interactivo

---

## [0.1.0] — 2026-03-24

### Añadido
- Repo creado: estructura enterprise inicial
- `pyproject.toml`, `Makefile`, `.gitignore`
- Estructura `src/`, `tests/`, `docs/`, `datos/`, `docker/`

---

_Última actualización: 24 marzo 2026 — 22:55 CET_
