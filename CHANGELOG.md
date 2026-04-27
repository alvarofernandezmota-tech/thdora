# 📋 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [ROADMAP](ROADMAP.md) · [Índice docs](docs/INDEX.md)

---

## [v0.16.2] — 27 abril 2026 (noche)

### 🐛 Bugfix — B-NEW3, B-NEW5, B-NEW6

#### Resumen de sesión
Sesión nocturna de auditoría y cierre. Se identifican y corrigen tres bugs
nuevos detectados al revisar el código en profundidad. Ningún cambio en la API
ni en la base de datos. Sin cambios en `.env`.

---

#### B-NEW3 — `habitos.py` · `_kb_edit_hab_fields` · nombre truncado

**Problema:** `_kb_edit_hab_fields` usaba `habit[:15]` en los `callback_data`
(`hedit_name_` y `hedit_val_`). Los hábitos con nombre > 15 chars no se
encontraban al parsear de vuelta porque el nombre estaba truncado.

**Contexto:** `_kb_hab_actions` y `_kb_hab_confirm` ya tenían este fix (FIX B3
documentado en v0.15.x). `_kb_edit_hab_fields` lo había quedado sin actualizar.

**Fix:** Eliminado `habit[:15]` → se usa el nombre completo igual que en
`_kb_hab_actions` y `_kb_hab_confirm`.

---

#### B-NEW5 — `main.py` · `_post_init` · scheduler no arrancaba en producción

**Problema:** `app.post_init = _post_init` no es el API correcto de
PTB v20+. La asignación directa puede fallar en producción haciendo que
el scheduler (APScheduler) no arranque de forma fiable.

**Fix:**
```python
# ANTES (incorrecto para PTB v20+):
app = ApplicationBuilder().token(token).persistence(persistence).build()
app.post_init = _post_init

# DESPUÉS (correcto):
app = (
    ApplicationBuilder()
    .token(token)
    .persistence(persistence)
    .post_init(_post_init)   # API correcto PTB v20+
    .build()
)
```
Bump de versión del bot a **v4.3**.

---

#### B-NEW6 — `keyboards.py` · `_kb_horas_franja("noche")` · mezcla visual 22-23 y 00-05

**Problema:** La franja noche incluye horas 22-23 y 00-05 en un único bloque
sin distinción visual. El usuario podía confundirse pensando que 00:00 es
media noche del día siguiente.

**Fix:** Dos bloques separados:
1. Fila: `22:00 | 23:00`
2. Separador visual: botón `── Madrugada ──` (informativo, `callback_data="noop_separator"`)
3. Filas de 4: `00:00 | 01:00 | 02:00 | 03:00` / `04:00 | 05:00`

---

### 📦 Archivos de esta sesión

| Archivo | Cambio |
|---|---|
| `src/bot/handlers/habitos.py` | 🐛 Fix B-NEW3: eliminado `habit[:15]` en `_kb_edit_hab_fields` |
| `src/bot/main.py` | 🐛 Fix B-NEW5: `ApplicationBuilder().post_init()` + bump v4.3 |
| `src/bot/keyboards.py` | 🐛 Fix B-NEW6: separador visual noche/madrugada |
| `CHANGELOG.md` | 📝 Esta entrada |
| `docs/diarios/2026-04-27.md` | 📝 Cierre sesión nocturna |

### ⚠️ Nota de despliegue
`git pull` en Acer + `docker compose restart bot`. No requiere cambios en `.env` ni API.

### 🧪 Checklist de prueba — v0.16.2

```
B-NEW3 — Hábito con nombre largo (> 15 chars)
[ ] Registra un hábito con nombre largo (ej: "Meditación matutina")
[ ] Pulsa ✏️ → debe mostrar botones con nombre completo, no truncado
[ ] "Cambiar valor" → guarda correctamente
[ ] "Cambiar nombre" → cambia correctamente

B-NEW5 — Scheduler arranca en producción
[ ] Reinicia el bot (docker compose restart bot)
[ ] /start → programa jobs diarios
[ ] Espera 2 min → log debe mostrar "⏰ Scheduler F12 iniciado"
[ ] Los recordatorios de cita se programan al crear una cita

B-NEW6 — Franja noche separada visualmente
[ ] /nueva → Noche → teclado muestra 22:00 | 23:00 en primera fila
[ ] Separador "── Madrugada ──" visible entre 23:00 y 00:00
[ ] Filas de madrugada: 00:00 01:00 02:00 03:00 / 04:00 05:00
[ ] Pulsar separador no hace nada (noop_separator)
```

### ⏩ Siguiente — Tarea 1.2
**Objetivo:** Mostrar huecos disponibles antes de mover/editar una cita.
- Al pulsar ✏️ → Hora: mostrar slots libres del día como botones.
- Reutilizar `_build_day_schedule` de `nlp.py`.
- Botones de franja → horas libres de esa franja.
- Si no hay huecos: mensaje claro + opción escribir hora manual.
- Integrar `_check_and_show_conflict` al final.

---

## [v0.16.1] — 27 abril 2026 (tarde)

### 🐛 Bugfix — Emoji franja Tarde (B1) + hora_ver_cuartos (B6)

#### Resumen de sesión
Sesión de bugs en el flujo `/nueva`. Se corrigen dos inconsistencias visuales/lógicas en el selector de hora por franjas. Ningún cambio en la API ni en la base de datos.

---

#### B1 — `citas.py` · `nueva_recv_franja` · emoji incorrecto

**Problema:** `franja_labels["tarde"]` devolvía `"🏆 Tarde"` mientras que `_kb_franjas()` en `keyboards.py` mostraba `"🌆 Tarde"`. El usuario veía un emoji diferente al pulsar el botón y al ver la confirmación.

**Fix:** `franja_labels` actualizado → `{"manana": "🌅 Mañana", "tarde": "🌆 Tarde", "noche": "🌙 Noche"}` para ser idéntico al teclado.

---

#### B6 — `citas.py` · `nueva_recv_hora_punto` · `hora_ver_cuartos` ignoraba hora seleccionada

**Problema:** Al pulsar el botón "Ver cuartos" tras elegir una hora (ej: 17:00), el bot ignoraba `nueva_hora_temp` y mostraba los cuartos del inicio de franja (14:xx para Tarde, 6:xx para Mañana, 22:xx para Noche).

**Fix:**
```python
# ANTES (bug):
hora_inicio = {"manana": 6, "tarde": 14, "noche": 22}[franja]

# DESPUÉS (fix B6):
_franja_inicio = {"manana": 6, "tarde": 14, "noche": 22}
hora_inicio = context.user_data.get("nueva_hora_temp") or _franja_inicio.get(franja, 6)
```

---

### 📦 Archivos de esta sesión

| Archivo | Cambio |
|---|---|
| `src/bot/handlers/citas.py` | 🐛 Fix B1 (emoji) + Fix B6 (hora_ver_cuartos) |
| `CHANGELOG.md` | 📝 Esta entrada |
| `ROADMAP.md` | 📝 B1/B6 añadidos al historial |
| `docs/diarios/2026-04-27.md` | 📝 Sesión 2 + checklist de pruebas completo |

### ⚠️ Nota de despliegue
`git pull` en Acer + `docker compose restart bot`. No requiere cambios en `.env` ni API.

---

## [v0.16.0] — 23 abril 2026 (tarde)

### 🔧 UX — Confirmación de borrado de cita muestra nombre + hora

#### Resumen de sesión
Sesión corta pero limpia. Un fix de UX real (tarea 1.3 del Bloque 1) y
documentación al día. El bot ya muestra exactamente qué cita vas a borrar
antes de pedirte confirmación.

---

### 📦 Archivos de esta sesión

| Archivo | Cambio |
|---|---|
| `src/bot/handlers/citas.py` | 🔧 cb_apt_delete muestra nombre+hora antes de confirmar |
| `ROADMAP.md` | 📝 1.3 ✅, versión v0.16.0, siguiente → 1.2 |
| `CHANGELOG.md` | 📝 Esta entrada |

---

## [v0.15.2] — 14 abril 2026 (tarde)

### ✨ NLP v2 — Cache, contexto semana, desambiguación y cierre de proyecto

---

## [v0.15.1] — 14 abril 2026

### 🔧 Fix — Conflicto de cita alineado entre API, bot /nueva y editar hora

---

## [v0.15.0] — 14 abril 2026

### ✨ Mejoras de calidad — Solapamiento real, horario visual, rendimiento y tests

---

## [v0.14.0] — 14 abril 2026
### ✨ Modo Toki: contexto real + menú en intent desconocido

---

## [v0.13.0] — 14 abril 2026
### ✨ UX, Persistencia y Personalidad

---

## [v0.12.0] — 14 abril 2026
- groq_router.py completo, handlers/nlp.py, NLP_ARQUITECTURA.md.

---

## [v0.11.0] — 13 abril 2026
- UserConfig SQLite, APScheduler, /config con notificaciones.

---

## [v0.10.0] — Abril 2026
- Bot v4 modular + UX avanzada.

---

## [v0.9.0] — Marzo 2026
- SQLiteLifeManager CRUD + FastAPI 14 endpoints.

---

## [v0.1–0.8] — Febrero–Marzo 2026
- Arquitectura base, FastAPI REST, Bot Telegram v1–v3.

---

_Última actualización: 27 abril 2026 — 22:28 CEST_
