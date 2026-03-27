# 📝 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [ROADMAP](ROADMAP.md) · [Arquitectura](docs/architecture/ARCHITECTURE.md)

Todos los cambios importantes del proyecto se documentan aquí.  
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [0.7.1] — 2026-03-27 (noche)

### Añadido
- `src/api/deps.py` — singleton `get_manager()` con `lru_cache(maxsize=1)`
- `src/api/routers/appointments.py` — nuevo endpoint `PUT /appointments/{date}/{index}` (editar cita)
- `src/api/routers/habits.py` — nuevos endpoints `DELETE /habits/{date}/{habit}` y `PUT /habits/{date}/{habit}`
- `src/bot/api_client.py` — métodos nuevos: `update_appointment`, `delete_habit`, `update_habit`, `_put()`
- `src/bot/handlers.py` — **reescritura completa v2:**
  - Flujo `/nueva` con **5 pasos** (fecha → hora → nombre → tipo → notas)
  - Fechas flexibles con `dateparser` (`hoy`, `mañana`, `ayer`, `27/03`, `lunes`…)
  - `/citas` con botones inline 🗑️ Borrar / ✏️ Editar por cita
  - `/habitos` con botones inline 🗑️ / ✏️ / ➕ por hábito
  - Confirmación antes de borrar cita o hábito
  - Hábitos acumulables: `+2L` suma al valor existente (detecta unidades)
  - 4 ConversationHandlers: `nueva_cita`, `registrar_habito`, `editar_cita`, `editar_habito`
- `src/bot/main.py` — v2: registra los 4 ConversationHandlers + 6 CallbackQueryHandlers globales + `_route_free_text` para acumulación
- `docs/modules/bot.md` — documentación completa del módulo bot
- `docs/auditoria/2026-03-27.md` — auditoría de la sesión

### Bugs conocidos (pendientes de fix)
- `/nueva` paso 4 (tipo) se salta: el nombre se captura bien en paso 3 pero el ConversationHandler pasa directo a paso 5 sin mostrar el teclado inline de tipo
- Contexto `acum_hab_nombre` puede quedar suelto en `user_data` e interceptar texto en `/habitos`

### Probado en vivo
- ✅ `/start` — menú nuevo con fechas aceptadas
- ✅ `/nueva` — 5 pasos (paso tipo con bug menor)
- ✅ `/citas` — botones inline por cita
- ✅ `/habitos` — botones inline por hábito
- ✅ `/habito` — teclado + acumulación funcionan
- ✅ `/resumen` — citas + hábitos
- ✅ `dateparser` instalado y activo

### Dependencias nuevas
- `dateparser==1.4.0` — parseo de fechas en lenguaje natural

---

## [0.7.0] — 2026-03-27

### Añadido
- `src/bot/api_client.py` — cliente HTTP asíncrono con `ThdoraApiClient`
- `src/bot/handlers.py` — handlers v1 (4 pasos, sin inline buttons)
- `src/bot/main.py` — entrypoint con health check al arrancar

---

## [0.6.1] — 2026-03-25

### Añadido
- `GET /summary/{date}` — endpoint de resumen diario (citas + hábitos) — **cierra Fase 6**

---

## [0.6.0] — 2026-03-25

### Limpieza y reorganización
- Eliminados 8 ficheros zombie de `src/core/` y `src/api/` raíz
- Coverage total subió de 45% a 87%
- Tests reorganizados en `unit/` + `integration/` + `e2e/`

---

## [0.5.0] — 2026-03-24 (noche)

### Añadido
- `src/core/impl/memory_lifemanager.py`, `src/core/impl/json_lifemanager.py`
- `src/api/routers/appointments.py`, `src/api/routers/habits.py`
- Tests unitarios e integración (61 tests)

---

## [0.4.0] — 2026-03-24

### Añadido
- `docs/INDEX.md`, ADR-003, ADR-004

---

## [0.3.0] — 2026-03-24

### Añadido
- ADR-001, ADR-002, arquitectura, módulos core y api

---

## [0.2.0] — 2026-03-24

### Añadido
- `AbstractLifeManager`, `MemoryLifeManager`, 13 tests

---

## [0.1.0] — 2026-03-24

### Añadido
- Repo inicial: estructura base, `pyproject.toml`, `Makefile`

---

_Última actualización: 27 marzo 2026 — 21:40 CET_
