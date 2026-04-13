# 🧭 THDORA — Cómo proceder

> Guía de trabajo para retomar el proyecto después de un descanso.
> Estado al día, siguiente paso claro, sin buscar contexto.
>
> **Navegación:** [README](README.md) · [ROADMAP](ROADMAP.md) · [Índice docs](docs/INDEX.md)

---

## 📍 Estado actual — 13 abril 2026

**Versión:** v0.12.0  
**F12 Notificaciones proactivas: 100% implementado.**  
Todo el bot probado en vivo y funcionando al 100% hasta F11.  
F12 está escrito y listo para probar en casa.

### ✅ Funciona hoy
- `/start` `/citas` `/habitos` `/habito` `/nueva` `/semana` `/resumen` `/config` `/cancelar`
- CRUD completo de citas y hábitos con SQLite
- Franjas horarias en `/nueva`
- Conflicto de hora y conflicto de hábito gestionados
- `/config → Hábitos` — configura tipos y botones rápidos
- `/config → Notificaciones` — activar/desactivar resumen diario, avisos de cita, evening log; cambiar horas y offsets
- **Scheduler APScheduler** arranca al iniciar el bot:
  - Job cron `daily_summary` → resumen de citas a la hora configurada (default 08:00)
  - Job cron `evening_log`   → recordatorio hábitos (default 22:00)
  - Jobs one-shot `apt_reminder_*` → aviso X min antes de cada cita
- Al crear una cita se programan sus avisos automáticamente
- Al borrar/editar una cita los avisos se cancelan/reprograman

### ❌ No implementado todavía
- **Docker / despliegue 24/7** (F10)
- **Multi-usuario** (F11)
- **IA conversacional** (F13)
- **Tracking personal** (F14)
- **Gamificación** (F15)

---

## ⏭️ Siguiente paso — F10 Docker / despliegue 24/7

F12 está completo. El siguiente paso es F10 (Docker y despliegue en servidor)  
o bien probar F12 a fondo primero (recomendado).

---

## 🧪 Probar F12 ahora mismo (paso a paso)

> Sigue este orden. Si algo falla, anota el error y se corrige.

### 0. Prerequisito: instalar APScheduler

```bash
source .venv/bin/activate
pip install apscheduler
# Añadir al requirements.txt si no está:
echo "apscheduler>=3.10" >> requirements.txt
```

### 1. Arrancar

Abre **dos terminales** en `/home/alvaro/projects/thdora`:

```bash
# Terminal 1
source .venv/bin/activate && make run-api

# Terminal 2
source .venv/bin/activate && make run-bot
```

Deberías ver en el bot:
```
✅ API de THDORA disponible en http://localhost:8000
⏰ Scheduler F12 iniciado
🤖 THDORA bot v4.0 arrancando (polling)…
```

### 2. Comprobar API nueva

```bash
# Debe devolver config por defecto del usuario (se crea sola al primer GET)
curl http://localhost:8000/user_config/TU_TELEGRAM_ID

# Respuesta esperada:
# {"user_id":"...","daily_summary_enabled":true,"daily_summary_time":"08:00",...}
```

> Tu Telegram ID: envía `/start` al bot, el log lo muestra, o usa @userinfobot en Telegram.

### 3. Probar /config → Notificaciones

En Telegram:
1. `/config` → aparece menú con **🧠 Hábitos** y **🔔 Notificaciones**
2. Pulsa **Notificaciones** → verás estado actual de cada opción
3. Toggle **Resumen diario** → ✅/❌ cambia al instante
4. Pulsa **⏰ Hora resumen** → elige una hora próxima (ej. `23:00` si son las 22:55)
5. Pulsa **⏰ Minutos antes de cita** → elige `5 min`
6. Guarda y vuelve al menú

### 4. Probar aviso de cita

```
1. /nueva
2. Pon la fecha de hoy
3. Elige una hora 3-5 min en el futuro (ej. si son las 22:45 → pon 22:50)
4. Nombre: "Test aviso"
5. Tipo: personal
6. /skip en notas
```

Espera y a los 5 min antes de esa hora deberías recibir:
```
🔔 Recordatorio
En 5 min tienes:
  ⏰ 22:50 — Test aviso
```

### 5. Probar cancel al borrar

- Ve a `/citas hoy` → borra la cita anterior → el job se cancela (no llega aviso)

### 6. Probar resumen diario

- Ve a **Notificaciones** → pon la hora resumen 2 min en el futuro
- Espera y deberías recibir el resumen de citas del día

### 7. Probar evening log igual

- Toggle **Evening log** activo → pon hora 2 min en el futuro → esperar aviso

---

## 🛠️ Arranque rápido (resumen)

```bash
# En /home/alvaro/projects/thdora
source .venv/bin/activate

# Terminal 1
make run-api

# Terminal 2
make run-bot
```

---

## 📁 Estructura del proyecto

```
thdora/
├── src/
│   ├── core/                  ← lógica de negocio pura
│   │   ├── abstract/          ← AbstractLifeManager
│   │   └── impl/              ← SQLiteLifeManager (activo)
│   ├── db/
│   │   ├── models.py          ← tablas: Appointment, Habit, HabitConfig, UserConfig (F12)
│   │   └── base.py            ← init_db()
│   ├── api/
│   │   ├── main.py            ← FastAPI app v0.12.0
│   │   └── routers/
│   │       ├── appointments.py
│   │       ├── habits.py
│   │       ├── habit_config.py
│   │       ├── summary.py
│   │       └── user_config.py     ← GET + PUT /user_config/{user_id}  [F12 ★]
│   └── bot/
│       ├── main.py            ← entrypoint v4.0 + arranca scheduler [F12 ★]
│       ├── api_client.py      ← cliente HTTP async (incl. get/update_user_config) [F12 ★]
│       ├── keyboards.py       ← teclados inline + _kb_config_menu, _kb_notif_* [F12 ★]
│       ├── scheduler.py       ← APScheduler: daily_summary, evening_log, apt_reminder [F12 ★]
│       ├── utils/
│       │   ├── dates.py
│       │   └── accum.py
│       └── handlers/
│           ├── menu.py
│           ├── citas.py           ← engancha schedule/cancel en crear/borrar/editar [F12 ★]
│           ├── habitos.py
│           ├── semana.py
│           ├── config.py          ← menú raíz + rama Hábitos + rama Notificaciones [F12 ★]
│           └── common.py
├── data/
│   └── thdora.db              ← SQLite (no versionado)
├── docs/
├── Makefile
├── requirements.txt
└── .env.example
```

> Los ficheros marcados con **[F12 ★]** son los añadidos o modificados en esta feature.

---

## 📖 Documentación disponible

| Doc | Para qué sirve |
|-----|---------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Estructura y decisiones de diseño |
| [docs/FLUJOS_DETALLADOS.md](docs/FLUJOS_DETALLADOS.md) | Estados, transiciones, casos borde de todos los flujos |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | Todos los endpoints con ejemplos |
| [docs/CONVENCIONES.md](docs/CONVENCIONES.md) | Patrones callback_data, variables entorno, orden handlers |
| [docs/F12_NOTIFICACIONES_DESIGN.md](docs/F12_NOTIFICACIONES_DESIGN.md) | Diseño completo de F12 |
| [docs/INDEX.md](docs/INDEX.md) | Mapa completo de toda la documentación |

---

## 📅 Convenciones rápidas

```bash
# Commits
git commit -m "feat(F12): descripción"
git commit -m "fix: descripción"
git commit -m "docs: descripción"

# Prefijos callback_data
ad_  adc_         → borrar/confirmar cita
ae_              → editar cita
hd_  hdc_        → borrar/confirmar hábito
he_              → editar hábito
ha_              → sumar a hábito
hval_            → valor rápido hábito
hconf_           → resolver conflicto hábito
cfg_             → config menú raíz
notif_           → acciones de notificaciones
# Lista completa → docs/CONVENCIONES.md
```

---

_Última actualización: 13 abril 2026 — 22:35 CEST_
