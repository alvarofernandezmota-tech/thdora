# 🧠 Sesión 28 marzo 2026 — Visión Plataforma Unificada

**Fecha:** Sábado 28 marzo 2026, ~15:00 CET  
**Participantes:** Álvaro + Perplexity  
**Estado bot:** v3.2 corriendo en `main` con F9.3 + F9.4  

---

## 🎯 Decisión clave de la sesión

> **THDORA es la única fuente de verdad.**  
> Todo lo que hasta ahora vivía en YAMLs manuales, Markdown y tracking personal  
> pasa a vivir aquí — accesible desde el bot, desde la API REST y desde VS Code.

```
FastAPI (backend)
    │
    ├── 📅 Citas         →  data/appointments/YYYY-MM-DD.yaml
    ├── 📊 Hábitos       →  data/habits/YYYY-MM-DD.yaml
    ├── 📈 Tracking      →  data/tracking/YYYY-MM-DD.yaml
    └── 📋 Diarios       →  docs/diarios/YYYY-MM-DD.md
         │
         ├── Bot Telegram   →  móvil (Álvaro)
         ├── API REST        →  Claude / Perplexity / scripts
         └── YAML / MD       →  VS Code (lectura directa)
```

**Cada dato entra una sola vez** — desde el bot, la API o VS Code — y está disponible en los tres sitios.

---

## 📋 Módulos definidos

### 1. 📅 Agenda (ya existe — ampliar)
- Citas con selección de hora por franjas (🌅 🌆 🌙)
- Citas multi-día: cada día con su propio horario o el mismo
- Vista día, semana, mes

### 2. 📊 Hábitos (ya existe — ampliar)
- Hábitos multi-día con toggle por día (ej: domingo libre)
- Registro guiado rápido
- Vista semanal de hábitos (tabla)
- Hábito del día con valor diferente por día

### 3. 📈 Tracking personal (nuevo módulo)
- Migración del tracking YAML manual → API
- Campos: sueño, ejercicio, THC, tabaco, agua, humor, alimentación, estudio, proyecto
- Formulario guiado diario (un campo tras otro)
- Dashboard semanal — tabla visual de progreso
- Histórico — tendencias, racha de días, mejor semana
- Recordatorio automático si no se ha registrado
- Sistema de puntuación diaria (fórmula ya definida en PERSONAL-DATA-PLATFORM.md)

---

## 🖥️ Diseño de menús propuesto

### `/start` — Menú principal
```
👋 Hola, soy THDORA — Sáb 28 mar
Tu asistente personal de vida

[📅 Citas]      [📊 Hábitos]
[📋 Semana]     [📝 Resumen]
[➕ Nueva cita] [✏️ Hábito]
[📈 Tracking]   [⚙️ Config]
```

### Vista Citas — barra de navegación
```
[◀️]  [Sáb 28 mar]  [▶️]
[➕ Nueva]  [📊 Hábitos]
[📋 Semana]  [🏠 Menú]
```
- El botón central muestra la FECHA REAL del día visible (no "Hoy" fijo)
- `➕ Nueva` abre el flujo de nueva cita directamente (sin /nueva)

### Vista Hábitos — barra de navegación
```
[◀️]  [Sáb 28 mar]  [▶️]
[✏️ Hábito]  [📅 Citas]
[📋 Semana]  [🏠 Menú]
```

### Vista Semana
```
[◀️ Semana ant.]  [Semana sig. ▶️]
[📅 Esta semana]  [🏠 Menú]
+ toggle multi-día para cita/hábito repetido
```

---

## ⏰ Selección de hora por franjas (F9.5)

Al crear una cita, en vez de escribir la hora:

```
1. Elegir franja:
   [🌅 Mañana 6-14]  [🌆 Tarde 14-22]  [🌙 Noche 22-6]

2. Elegir hora en punto de la franja:
   [06:00] [07:00] [08:00] [09:00]
   [10:00] [11:00] [12:00] [13:00]

3. Opcional — ver cuartos:
   [🕐 Ver :00 :15 :30 :45]

4. Fallback siempre disponible:
   [✏️ Escribir hora exacta]
```

---

## 📅 Cita multi-día (F9.5)

```
Selecciona los días:
[Lun 30 ✅] [Mar 31 ☐] [Mié 1 ✅]
[Jue 2 ☐]  [Vie 3 ☐]  [Sáb 4 ✅]  [Dom 5 ☐]

Opciones de horario:
[⏰ Mismo horario para todos]
[🕐 Horario diferente por día]

[✅ Crear en 3 días seleccionados]
```

---

## 📊 Hábito multi-día (F9.5)

```
Selecciona los días:
[Lun 30 ✅] [Mar 31 ✅] [Mié 1 ✅]
[Jue 2 ✅]  [Vie 3 ✅]  [Sáb 4 ✅]  [Dom 5 ☐]  ← domingo libre

Opciones de valor:
[📊 Mismo valor para todos]
[✏️ Valor diferente por día]

[✅ Registrar en 6 días seleccionados]
```

---

## 📈 Vista semanal unificada (idea)

Una vista `/semana` que muestre tanto citas como hábitos juntos:

```
📋 Semana 30 mar — 5 abr

Lun 30  📅2  📊ejercicio✅  sueño:7h
Mar 31  📅1  📊—
Mié 1   📅3  📊ejercicio✅  thc:1
Jue 2   —    📊sueño:6h
Vie 3   📅1  📊ejercicio✅
Sáb 4   —    —
Dom 5   —    —
```

---

## 🗺️ Roadmap actualizado

| Feature | Descripción | Estado |
|---------|-------------|--------|
| F9.1 | Bot base + API + navegación | ✅ Done |
| F9.2 | ConversationHandlers + edición | ✅ Done |
| F9.3 | UI unificada — Menú, volver, cambio vistas | ✅ Done |
| F9.4 | Horas clicables + vista detalle cita | ✅ Done |
| **F9.5** | **Franjas horarias + cita multi-día + hábito multi-día + fecha real en nav** | 🔜 Next |
| **F9.6** | **Módulo Tracking — API + bot + formulario guiado** | 🔜 |
| **F9.7** | **Vista semanal unificada (citas + hábitos + tracking)** | 🔜 |
| **F9.8** | **Vista mes — calendario visual** | 🔜 |
| **F9.9** | **Dashboard tracking — tendencias + racha + nota diaria** | 🔜 |
| F10 | Alertas automáticas (scheduler) | 🔜 |
| F11 | Migración YAML personal → API | 🔜 |

---

## 🐛 Bug conocido pendiente

```python
# handlers.py línea ~562 — _show_semana()
# ❌ nav_kb.inline_keyboard devuelve tuplas, no listas
full_kb = InlineKeyboardMarkup([btn_days[:4], btn_days[4:]] + nav_kb.inline_keyboard)

# ✅ Fix:
full_kb = InlineKeyboardMarkup([btn_days[:4], btn_days[4:]] + [list(row) for row in nav_kb.inline_keyboard])
```
→ Se corrige en el commit de F9.5

---

_Sesión documentada: 28 marzo 2026 ~15:04 CET_
