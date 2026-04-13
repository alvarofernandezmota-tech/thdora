# 🔔 F12 — Notificaciones proactivas — Diseño completo

> Documento de diseño previo a la implementación.
> Todo el flujo, tablas, mensajes y orden de ficheros definidos aquí.
>
> **Navegación:** [README](../README.md) · [ROADMAP](../ROADMAP.md) · [ARCHITECTURE](ARCHITECTURE.md)

---

## Objetivo

Convertir THDORA de una agenda **pasiva** (el usuario pregunta) a un asistente **proactivo** (THDORA avisa sin que se lo pidan).

---

## Funcionalidades incluidas

### 1. Resumen diario
- A una hora configurable (default `08:00`) el bot manda las citas del día
- Si no hay citas: mensaje motivacional
- Activable/desactivable

### 2. Avisos antes de cada cita
- Offsets configurables: `60min`, `30min`, `15min` (toggles individuales)
- Se pueden combinar: avisar a los tres, a uno solo, o ninguno
- Activable/desactivable globalmente

### 3. Confirmación de asistencia (opcional)
- En el mensaje del aviso, añade botones `[✅ Voy]` `[🗑️ Cancelar cita]`
- Configurable como preferencia predeterminada
- Si se pulsa `Cancelar cita` → borra la cita y confirma

### 4. Resumen nocturno de hábitos (extensión futura)
- A una hora configurable (default `22:00`) recuerda registrar los hábitos del día
- Muestra los hábitos que aún no tienen registro hoy
- Activable/desactivable de forma independiente

---

## Tabla `user_config`

```python
class UserConfig(Base):
    __tablename__ = "user_config"

    id: int                      # PK autoincrement
    user_id: str                 # Telegram user_id — preparado para multi-usuario

    # ── Resumen diario ──────────────────────────────────────
    daily_summary_enabled: bool  # default=True
    daily_summary_time: str      # default="08:00"   formato HH:MM

    # ── Avisos de cita ────────────────────────────────────
    notif_enabled: bool          # default=True
    notif_offsets: str           # default="60,30,15"  minutos, separados por coma

    # ── Confirmación de asistencia ──────────────────────────
    notif_ask_confirm: bool      # default=False

    # ── Resumen nocturno de hábitos ───────────────────────
    evening_log_enabled: bool    # default=True
    evening_log_time: str        # default="22:00"   formato HH:MM

    # ── Zona horaria ──────────────────────────────────────
    timezone: str                # default="Europe/Madrid"
```

### Valores predeterminados

| Campo | Default | Razón |
|-------|---------|-------|
| `daily_summary_enabled` | `True` | activo desde el primer día |
| `daily_summary_time` | `"08:00"` | antes de salir de casa |
| `notif_enabled` | `True` | activo desde el primer día |
| `notif_offsets` | `"60,30,15"` | los tres avisos |
| `notif_ask_confirm` | `False` | no invasivo por defecto |
| `evening_log_enabled` | `True` | activo desde el primer día |
| `evening_log_time` | `"22:00"` | al final del día |
| `timezone` | `"Europe/Madrid"` | zona del desarrollador |

**Upsert automático:** `GET /user_config/{user_id}` crea la fila con defaults si no existe. El usuario nunca ve un error por "no configurado".

---

## Arquitectura del scheduler

```
Bot arranca
    │
    ├── _check_api()
    ├── build_app()              ← registra handlers (sin cambios)
    └── start_scheduler(app)     ← NUEVO — arranca APScheduler

Scheduler corre en paralelo (asyncio)
    │
    ├── Job: "daily_summary_{user_id}"
    │     └── Cada día a daily_summary_time
    │           → GET /user_config/{user_id}
    │           → GET /appointments/{today}
    │           → Manda resumen al usuario
    │
    ├── Job: "evening_log_{user_id}"
    │     └── Cada día a evening_log_time
    │           → GET /habits/{today}
    │           → Manda lista de hábitos sin registrar hoy
    │
    └── Jobs por cita: "notif_{apt_id}_{offset}min"
          └── Se crean al CREAR o EDITAR una cita
                → Para cada offset en notif_offsets:
                    hora_cita − offset → job puntual one-shot
                → Al BORRAR la cita → cancela sus jobs
```

---

## Flujo `/config` rediseñado

```
/config
    │
    ▼
┌─────────────────────────────────────┐
│  ⚙️ ¿Qué quieres configurar?     │
│  [💪 Hábitos]  [🔔 Notificaciones]  │  ← CFG_MENU
└─────────────────────────────────────┘
    │                    │
    ▼                    ▼
Flujo Hábitos      Flujo Notificaciones
(sin cambios)      (nuevo)


Pantalla Notificaciones:
─────────────────────────────────────────
🔔 Configuración de notificaciones

Resumen diario    ✅ 08:00
Avisos de cita    ✅ 60min + 30min + 15min
Confirmar asist.  ❌ desactivado
Resumen hábitos   ✅ 22:00

[🕐 Cambiar hora resumen]      ← abre NOTIF_HORA_SUMMARY
[🔔 / 🔕 Toggle resumen]         ← toggle instantáneo
[⏱️ Cambiar avisos cita]       ← abre NOTIF_OFFSETS
[❓ Toggle confirmación]       ← toggle instantáneo
[🌙 Cambiar hora hábitos]      ← abre NOTIF_HORA_EVENING
[🌙 / ❌ Toggle resumen hábitos] ← toggle instantáneo
[🏠 Menú]
─────────────────────────────────────────

Cambiar hora (NOTIF_HORA_SUMMARY / NOTIF_HORA_EVENING):
    [06:00][07:00][08:00][09:00][10:00]
    [20:00][21:00][22:00][23:00][✏️ Exacta]

Cambiar offsets (NOTIF_OFFSETS):
    [✅ 60min] [✅ 30min] [✅ 15min]
    [➕ Añadir otro offset]  ← escribe número de minutos
    [✅ Guardar]
```

---

## Estados ConversationHandler

```
CFG_MENU             (nuevo) — raíz: elige Hábitos o Notificaciones

── Rama Hábitos (sin cambios) ────────────────────────
CFG_NOMBRE           — nombre del hábito
CFG_TYPE             — tipo (numeric/time/boolean/text)
CFG_UNIT             — unidad
CFG_QUICK            — botones rápidos

── Rama Notificaciones (nueva) ───────────────────────
NOTIF_MENU           — pantalla principal (toggles instantáneos)
NOTIF_HORA_SUMMARY   — seleccionar hora resumen diario
NOTIF_HORA_EVENING   — seleccionar hora resumen hábitos
NOTIF_OFFSETS        — pantalla toggles 60/30/15min + añadir
```

---

## Formatos de mensaje

### Resumen diario (08:00)

```
🌅 Buenos días, Álvaro
─────────────────────────
📅 Hoy lunes 13 de abril

🕙 09:00 · Gimnasio
🕚 10:30 · Médico · Dr. García
🕓 15:00 · Reunión trabajo

3 citas hoy · Buena suerte 💪
```
*Si no hay citas:* `Hoy tienes el día libre ✨`

### Aviso de cita — sin confirmación

```
🔔 Recordatorio · en 30 min
─────────────────────────
📅 Hoy lunes 13 abr · 10:30
🏥 Médico · Dr. García
📝 Revisión anual
```

### Aviso de cita — con confirmación

```
🔔 Recordatorio · en 30 min
─────────────────────────
📅 Hoy lunes 13 abr · 10:30
🏥 Médico · Dr. García
📝 Revisión anual

¿Confirmas asistencia?
[✅ Voy]  [🗑️ Cancelar cita]
```

### Resumen nocturno de hábitos (22:00)

```
🌙 Buenas noches, Álvaro
─────────────────────────
Aún no has registrado hoy:

  • Sueño
  • Agua
  • Ejercicio

[💪 Registrar ahora]
```
*Si todo registrado:* `✅ Todos los hábitos registrados hoy. ¡Gran día!`

---

## Orden de implementación

| # | Fichero | Cambio |
|---|---------|--------|
| 1 | `src/db/models.py` | + clase `UserConfig` con todos los campos y defaults |
| 2 | `src/core/impl/sqlite_lifemanager.py` | + `get_user_config(user_id)`, `upsert_user_config(...)` |
| 3 | `src/api/routers/user_config.py` | nuevo — `GET` + `PUT /user_config/{user_id}` |
| 4 | `src/api/main.py` | registrar router `user_config` |
| 5 | `src/bot/api_client.py` | + `get_user_config()`, `update_user_config()` |
| 6 | `src/bot/keyboards.py` | + `_kb_config_menu()`, `_kb_notif_menu(cfg)`, `_kb_notif_hora()`, `_kb_notif_offsets(cfg)` |
| 7 | `src/bot/handlers/config.py` | rediseño con `CFG_MENU` raíz + rama notificaciones |
| 8 | `src/bot/scheduler.py` | **nuevo** — APScheduler: job diario + evening log + jobs por cita |
| 9 | `src/bot/handlers/citas.py` | al crear/editar/borrar cita → reprogramar jobs del scheduler |
| 10 | `src/bot/main.py` | + `start_scheduler(app)` al arrancar |

---

## Impacto en ROADMAP

Esta feature cierra **F12 — Notificaciones proactivas** del roadmap.
Prepara el terreno para **F11 Multi-usuario** (el campo `user_id` ya está en `UserConfig`).

---

_Diseño cerrado: 13 abril 2026 — 21:13 CEST_
