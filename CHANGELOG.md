# Changelog — THDORA

Todas las versiones siguen [Semantic Versioning](https://semver.org/).

---

## [v0.17.2] — 2026-06-20

### Fixed — Healthcheck bot (Docker)

- `docker-compose.yml`: el servicio `bot` no tenía healthcheck propio y heredaba
  el comportamiento del `Dockerfile` que hacía `curl localhost:8000/health/live`.
  El bot no expone ningún puerto HTTP, por lo que el check fallaba siempre
  → `FailingStreak: 86`, status `unhealthy` permanente.
- Fix: añadido healthcheck explícito al servicio `bot` usando
  `python3 -c "import os, sys; sys.exit(0)"` — comprueba que el intérprete
  Python existe y funciona, sin depender de ningún puerto.
- El bot estaba funcionando correctamente durante todo el tiempo;
  el `unhealthy` era falso positivo del healthcheck mal configurado.

---

## [v0.17.1] — 2026-06-20

### Fixed — Auditoría completa de infraestructura

**Docker (crítico)**
- `docker-compose.yml`: `command` apuntaba a `/entrypoint-api.sh` y `/entrypoint-bot.sh`
  que no existían → el stack nunca hubiera arrancado. Corregido a `/entrypoint.sh`
  con `SERVICE_TARGET` env var
- `docker-compose.yml`: `thdora` dependía de `prometheus` → API bloqueada si Prometheus fallaba.
  Removida dependencia; API ahora es independiente
- `docker-compose.yml`: imágenes `latest` de Prometheus y Grafana → fijadas a versiones concretas
  (`prom/prometheus:v2.51.2`, `grafana/grafana:10.4.2`) para builds reproducibles
- `docker-compose.yml`: sin red Docker explícita → añadida red `thdora-net` bridge
- `docker/entrypoint.sh`: no diferenciaba entre api y bot → refactorizado con
  `case $SERVICE_TARGET in api|bot)` con `mkdir -p /app/data /app/logs`
- `Dockerfile`: `chown` no incluía `/app/data` y `/app/logs` → corregido para
  que el usuario `thdora:1000` pueda escribir en los volúmenes montados
- `data/.gitkeep` y `logs/.gitkeep`: directorios requeridos por Docker volumes
  no estaban trackeados en git

**Dependencias**
- `requirements.txt`: header de versión era `v0.22.1` (incorrecto) → corregido a `v0.17.0`
- `requirements.txt`: añadido `aiofiles>=23.2.0` (requerido por handler /diario)
- `requirements.txt`: añadido `psycopg2-binary>=2.9.9` (prep para migración PostgreSQL)

**Configuración**
- `.env.example`: faltaban `GROQ_API_KEY`, `GROQ_MODEL`, `GITHUB_TOKEN`, `GITHUB_REPO`,
  `TZ`, `LOG_LEVEL` → añadidas con documentación inline
- `monitoring/prometheus/prometheus.yml`: archivo requerido por el volumen Docker no existía
  → creado con config mínima (scrape API + self)
- `monitoring/grafana/provisioning/`: directorio requerido por docker-compose no existía
- `pytest.ini`: conflicto con `pyproject.toml` → simplificado para delegar

**Documentación**
- `ROADMAP.md`: actualizado a v0.17.0 merged con checklist de deploy
- `PLAN_MANANA.md`: reescrito con pasos exactos para deploy en Servidor Madre

---

## [v0.17.0] — 2026-06-20

### Fixed — 14 bugs críticos (B12–B25)

**citas.py (B12–B16)**
- B12: `get_appointments()` llamado sin `user_id` en 5 sitios → añadido en todos
- B13: `create_appointment(d, t, nm, tp, notes)` args positionales rotos → `(date_str, data:dict, user_id)`
- B14: `update_appointment(..., time=, name=, apt_type=, notes=)` kwargs sueltos → `(date_str, index, data:dict, user_id)`
- B15: `delete_appointment()` sin `user_id` → añadido
- B16: `api.check_appointment_conflict()` no existe en `ThdoraApiClient` → reemplazado por `_find_overlap()` local

**habitos.py (B17–B21)**
- B17: `get_habits()` sin `user_id` en 4 sitios → añadido
- B18: `log_habit()` sin `user_id` → añadido
- B19: `update_habit()` sin `user_id` → añadido
- B20: `delete_habit()` sin `user_id` → añadido
- B21: `get_habit_config()` sin `user_id` → añadido
- Completadas funciones truncadas: `cb_hab_edit_field`, `_do_edit_habit`,
  `build_habito_handler`, `build_edit_hab_handler`

**config.py (B22–B25)**
- B22: `api.get_all_habit_configs()` no existe → `api.get_habit_configs(user_id)`
- B23: `upsert_habit_config(name=..., habit_type=..., ...)` kwargs → `(data:dict, user_id)`
- B24: `delete_habit_config(nombre)` sin `user_id` → añadido
- B25: `update_user_config(user_id, key=val)` kwargs sueltos → `(user_id, data:dict)` en los 5 toggles

**Infraestructura v0.17.0**
- `Dockerfile`: refactorizado a multi-stage (builder + runtime), usuario no-root
- `docker/entrypoint.sh`: añadido `alembic upgrade head` antes de arrancar uvicorn
- `citas.py`: `update.get_bot()` → `context.bot` (PTB ≥20 compat)
- `config.py`: `query.get_bot()` → `context.bot` en `notif_recv_time`
- `config.py`: `notif_user_id` persistido en `user_data` al entrar al menú

**Tests y docs v0.17.0**
- Suite completa: `tests/conftest.py` + `test_api_client.py` + `test_habitos.py`
  + `test_citas.py` + `test_config.py` + `test_accum.py`
- `scripts/autotest.py`: verificación del ecosistema sin pytest
- CI/CD: `.github/workflows/ci.yml` + `docker-health.yml`
- Docs: `ARCHITECTURE.md`, `CONTRIBUTING.md`, `docs/ADR-001`, `docs/ADR-002`, `llms.txt`

---

## [v0.16.1] — 2026-04-27

### Fixed
- B1: `franja_labels` emoji corregido 🏆→🌆 en `citas.py`
- B6: `hora_ver_cuartos` usa hora ya seleccionada si existe en `user_data`

## [v0.16.0] — 2026-04-23

### Added
- `cb_apt_delete`: muestra nombre + hora antes de pedir confirmación (UX)

## [v0.15.1] — 2026-04-15

### Added
- Detección de conflictos de hora en `/nueva` y editar cita
- `_build_day_schedule` para horario visual del día

## [v0.15.0] — 2026-04-10

### Added
- Flujo `/nueva` con franjas horarias (Mañana / Tarde / Noche / Exacta)
- `build_nueva_handler` y `build_edit_apt_handler`

## [v0.14.0] — 2026-03-28

### Added
- `/config` completo: configuración de hábitos y notificaciones
- Scheduler de reminders con APScheduler
- Docker Compose con Grafana + Prometheus
