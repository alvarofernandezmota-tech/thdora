# CHANGELOG — THDORA

Todos los cambios relevantes del proyecto ordenados de más reciente a más antiguo.

---

## [v4.1.0] — 2026-04-14

### Fixed
- **`citas.py`**: `_parse_apt_callback()` usa `rsplit('_', 1)` para extraer
  `(date_str, index)` de callbacks `ae_`, `ad_`, `adc_` — evita romper con
  fechas que contienen guiones (`2026-04-13`).
- **`habitos.py`**: `_parse_hab_callback()` usa slice fijo `[:10]` / `[11:]`
  para extraer `(date_str, habit)` de callbacks `hd_`, `hdc_`, `he_`, `ha_`.
- **`scheduler.py`**: `apt.get('date') or apt.get('date_str', '')` — evita
  `WARNING: 'date'` al programar recordatorios de cita.
- **Flujo editar cita**: reescrito con botones (Hora / Nombre / Tipo / Notas).
  Elimina el uso de `/skip` en edición.
- **Flujo editar hábito**: reescrito con botones (Cambiar nombre / Cambiar valor).
- **`main.py`**: eliminado `cb_quick_config` como handler global — era
  entry_point de `build_config_handler()` y causaba conflicto de captura.
- **`main.py`**: `post_init` arranca el scheduler dentro del event loop de PTB
  (evita `RuntimeError: no running event loop`).
- **`menu.py`**: `cmd_start` llama a `schedule_user_jobs()` para programar los
  jobs diarios (daily_summary / evening_log) del usuario al arrancar.
- **`config.py`**: añadido botón 🗑️ Borrar por cada hábito configurado +
  estado `CFG_DEL_CONF` con confirmación.
- **`config.py`**: `_is_skip()` normaliza `/skip` y `skip` (con y sin barra)
  en pasos `CFG_UNIT` y `CFG_QUICK`.
- **`config.py`**: `notif_cancel_to_menu` registrado en `NOTIF_SET_TIME` y
  `NOTIF_SET_OFFSETS` — el botón ❌ Cancelar del teclado de horas ya funciona
  y vuelve al menú de notificaciones sin guardar.
- **`config.py`**: los toggles on/off de notificaciones ya **no reprograman**
  el scheduler; solo `notif_recv_time` lo hace al confirmar una hora nueva.
  Elimina la duplicación de jobs APScheduler.
- **`common.py`**: `error_handler` ahora notifica al usuario con
  `show_alert=True` cuando hay un error no controlado.
- **`handlers/__init__.py`**: eliminado export de `cb_quick_config`.

---

## [v4.0.0] — 2026-04-13

### Added
- Franjas horarias en `/nueva`: 🌅 Mañana / 🌆 Tarde / 🌙 Noche + cuartos.
- `build_edit_apt_handler()`: ConversationHandler dedicado a editar citas.
- `build_edit_hab_handler()`: ConversationHandler dedicado a editar hábitos.
- `build_config_handler()`: rama Hábitos + rama Notificaciones unificadas.
- Scheduler F12 con APScheduler: `daily_summary`, `evening_log`,
  `apt_reminder` (one-shot por cita con offsets configurables).
- Teclados de navegación semanal en `/semana`.
- `_kb_notif_menu()` con estado visible (✅/❌) y botones de hora.
- `COMO_PROCEDER.md` con guía de trabajo incremental.

### Changed
- Estados de ConversationHandlers reorganizados sin colisiones (rangos fijos).
- `keyboards.py` centraliza todos los teclados inline.

---

## [v3.x] — 2026-Q1

- Versión inicial funcional: citas, hábitos, resumen, semana.
- Sin scheduler, sin franjas, sin edición por botones.
