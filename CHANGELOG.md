# 📝 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [ROADMAP](ROADMAP.md)

Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [0.11.0] — 2026-04-13

### Probado en vivo — F9.7: Pruebas en entorno real + fix entry points menú ✅

**Todas las funciones del bot probadas en Telegram real por primera vez.**

#### Fix: entry points ConversationHandlers desde botones del menú

| Archivo | Cambio |
|---------|--------|
| `src/bot/handlers/citas.py` | Añadido `nueva_start_desde_boton` como entry point para `quick_nueva_*` |
| `src/bot/handlers/habitos.py` | Añadido `habito_start_desde_boton` como entry point para `quick_habito_*` |
| `src/bot/handlers/menu.py` | Eliminado `cb_quick_dispatch` — cada ConversationHandler captura su propio callback |
| `src/bot/handlers/__init__.py` | Reemplazado `cb_quick_dispatch` por `cb_quick_config` |
| `src/bot/main.py` | Reemplazado `cb_quick_dispatch` → `cb_quick_config`, patrón `^quick_config$` |

#### Resultados pruebas en vivo

| Función | Resultado | API |
|---------|-----------|-----|
| ➕ Nueva cita desde botón menú | ✅ Funciona | `POST /appointments/ → 201` |
| ➕ Nuevo hábito desde botón menú | ✅ Funciona | `POST /habits/ → 201` |
| Flujo franjas horarias `/nueva` | ✅ Funciona | — |
| Borrar cita | ✅ Funciona | `DELETE /appointments/ → 204` |
| Editar cita | ✅ Funciona | — |
| Editar/sumar hábito | ✅ Funciona | — |
| Navegación ◀️▶️ citas/hábitos | ✅ Funciona | — |
| `/semana` | ✅ Funciona | — |

---

## [0.10.0] — 2026-04-12

### Refactor — F9.6: handlers.py monolítico → módulos (✅ completado)

**`src/bot/handlers.py` (60KB, ~1500 líneas) eliminado y dividido en:**

| Módulo | Contenido |
|--------|----------|
| `src/bot/utils/dates.py` | `_parse_date_flex`, `_parse_date_arg`, `_date_label`, `_date_short`, `_greeting`, `_monday` |
| `src/bot/utils/accum.py` | `_accumulate_value`, `_clean_acum_context` |
| `src/bot/keyboards.py` | Todos los `_kb_*`, `_nav_keyboard`, constantes `TIPOS_CITA`, `FRANJAS`, `HABIT_TYPE_EMOJIS` |
| `src/bot/handlers/menu.py` | `cmd_start`, `cb_menu_home`, `cb_quick_dispatch` |
| `src/bot/handlers/citas.py` | `cmd_citas`, nav, detail, borrar/editar, `/nueva` + **FRANJAS HORARIAS** |
| `src/bot/handlers/habitos.py` | `cmd_habitos`, nav, `/habito`, borrar/editar/sumar |
| `src/bot/handlers/semana.py` | `cmd_semana`, `cb_semana_nav` |
| `src/bot/handlers/config.py` | `cmd_config`, `build_config_handler` |
| `src/bot/handlers/common.py` | `cmd_cancelar`, `cb_cancel_action`, `cmd_resumen`, `error_handler` |
| `src/bot/handlers/__init__.py` | Re-exporta todo — `main.py` sin cambios |

### Añadido — F9.5: Franjas horarias en /nueva

Flujo `/nueva` rediseñado con selección progresiva de hora:

```
Paso 1 → Fecha (texto libre: hoy, mañana, 27/03…)
Paso 2 → Franja: [🌅 Mañana 6-14] [🌆 Tarde 14-22] [🌙 Noche 22-6] [✏️ Exacta]
Paso 3 → Hora en punto: botones [06:00][07:00]…[13:00] + [🕐 Ver cuartos][✏️ Exacta]
Paso 4 → Cuartos (opcional): [HH:00][HH:15][HH:30][HH:45] + [✏️ Exacta]
Paso 5 → Nombre (texto libre)
Paso 6 → Tipo [Médica][Personal][Trabajo][Otra]
Paso 7 → Notas o /skip
```

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

### Añadido — F9.3: UI unificada
- Menú principal `/start` con botones inline
- Navegación ◀️▶️ en vistas `/citas` y `/habitos`
- Botón 🏠 Menú desde todas las vistas
- Cambio de vista Citas ↔ Hábitos desde la barra de navegación
- Botón 📋 Semana desde citas y hábitos

---

## [0.8.1] — 2026-03-28
### Mantenimiento — Auditoría + Limpieza repo
- Eliminado archivo basura `api_client, handlers y main"` (53KB pegado por error en raíz)
- Eliminado `.env~` (fichero vacío mal versionado)

---

## [0.8.0] — 2026-03-27 (noche)
### Añadido — F9: Persistencia SQLite
- `src/db/` — engine SQLAlchemy, modelos ORM, `SQLiteLifeManager`
- `data/thdora.db` — persistencia real

## [0.7.1] — 2026-03-27
### Añadido
- Endpoint `PUT /appointments/{date}/{index}`
- Endpoints `DELETE/PUT /habits/{date}/{habit}`
- `src/bot/handlers.py` v2: flujo `/nueva` 5 pasos, fechas flexibles, inline buttons

## [0.7.0] — 2026-03-27
### Añadido
- `src/bot/api_client.py` — cliente HTTP asíncrono `ThdoraApiClient`
- `src/bot/main.py` — entrypoint con health check

## [0.6.1] — 2026-03-25
### Añadido
- `GET /summary/{date}` — resumen diario (citas + hábitos)

## [0.6.0] — 2026-03-25
### Limpieza
- Eliminados 8 ficheros zombie, coverage 45% → 87%

## [0.5.0] — 2026-03-24 (noche)
### Añadido
- `MemoryLifeManager`, `JsonLifeManager`, 61 tests

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

_Última actualización: 13 abril 2026 — 20:43 CEST_
