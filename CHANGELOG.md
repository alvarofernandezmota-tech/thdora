# Changelog — THDORA

Todas las versiones siguen [Semantic Versioning](https://semver.org/).

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
- Completadas funciones truncadas: `cb_hab_edit_field`, `_do_edit_habit`, `build_habito_handler`, `build_edit_hab_handler`

**config.py (B22–B25)**
- B22: `api.get_all_habit_configs()` no existe → `api.get_habit_configs(user_id)`
- B23: `upsert_habit_config(name=..., habit_type=..., ...)` kwargs → `(data:dict, user_id)`
- B24: `delete_habit_config(nombre)` sin `user_id` → añadido
- B25: `update_user_config(user_id, key=val)` kwargs sueltos → `(user_id, data:dict)` en los 5 toggles

**Infraestructura**
- `Dockerfile`: refactorizado a multi-stage (builder + runtime), usuario no-root
- `docker/entrypoint.sh`: añadido `alembic upgrade head` antes de arrancar uvicorn
- `citas.py`: `update.get_bot()` → `context.bot` (PTB ≥20 compat)
- `citas.py`: `nueva_user_id` guardado en `nueva_start_desde_boton` para flujos por botón
- `config.py`: `query.get_bot()` → `context.bot` en `notif_recv_time`
- `config.py`: `notif_user_id` persistido en `user_data` al entrar al menú de notificaciones

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
