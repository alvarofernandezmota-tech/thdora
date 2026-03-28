# 🧠 Sesión 28 marzo 2026 — Visión Plataforma Unificada

**Fecha:** Sábado 28 marzo 2026, ~15:00 CET  
**Participantes:** Álvaro + Perplexity  
**Estado bot:** v3.2 corriendo en `main` con F9.3 + F9.4  

---

## 🎯 Visión definitiva

> **THDORA = fábrica de objetos personales a través de menús intuitivos.**  
> No es solo una agenda — es el espejo de tu vida.  
> El usuario nunca escribe comandos — solo pulsa botones.

### Evolución futura
- **Fase actual:** 100% botones inline
- **Siguiente:** Comprensión de texto natural (NLP)
- **Futuro:** Audio usuario → máquina + máquina → usuario

---

## 📦 Módulos — Fábrica de objetos

| Módulo | Objeto | Acciones |
|--------|--------|----------|
| 📅 Citas | `Appointment` | Crear, ver, editar, borrar, repetir multi-día |
| 📊 Hábitos | `HabitLog` | Registrar, editar, acumular, multi-día |
| 📈 Tracking | `DailyRecord` | Rellenar diario, ver dashboard, racha |
| 🕐 Timeline | `TimelineEntry` | Añadir entrada horaria, ver día |
| ⚙️ Config | `HabitConfig` | Crear tipo, editar, borrar |

---

## 🖥️ Diseño de menús 1 a 1

### `/start` — Menú principal
```
🌆 Buenas tardes, soy THDORA — Sáb 28 mar
⏰ Tienes 2 citas hoy

[📅 Citas]       [📊 Hábitos]
[📋 Semana]      [📝 Resumen]
[➕ Nueva cita]  [✏️ Hábito]
[📈 Tracking]    [⚙️ Config]
```
- Saludo contextual según hora (🌅 🌆 🌙)
- Aviso si hay citas hoy

### Vista Citas
```
📅 Citas — Sáb 28 mar

⏰ 10:00 — Médico [médica]
⏰ 17:00 — Gym [personal]

[◀️]  [Sáb 28 mar]  [▶️]
[➕ Nueva]    [📊 Hábitos]
[📋 Semana]  [🏠 Menú]
```

### Crear cita — franjas horarias
```
1️⃣ Franja:
[🌅 Mañana 6-14]  [🌆 Tarde 14-22]  [🌙 Noche 22-6]

2️⃣ Hora (ej: Mañana):
[06:00][07:00][08:00][09:00]
[10:00][11:00][12:00][13:00]
[🕐 Ver cuartos]  [✏️ Exacta]

3️⃣ Cuartos (opcional):
[10:00][10:15][10:30][10:45]
[✏️ Escribir exacta]

4️⃣ Nombre → texto libre
5️⃣ Tipo → [Médica][Personal][Trabajo][Otra]
6️⃣ Notas → texto libre o /skip
✅ Creada → [← Volver al día] [🏠 Menú]
```

### Cita multi-día
```
Selecciona días:
[Lun 30 ✅] [Mar 31 ☐] [Mié 1 ✅]
[Jue 2 ☐]  [Vie 3 ☐]  [Sáb 4 ✅]  [Dom 5 ☐]

[⏰ Mismo horario para todos]
[🕐 Horario diferente por día]
[✅ Crear en 3 días seleccionados]
```

### Vista Hábitos
```
📊 Hábitos — Sáb 28 mar

• ejercicio: 30min  [✏️][🗑️][➕]
• sueño: 8h         [✏️][🗑️][➕]

[◀️]  [Sáb 28 mar]  [▶️]
[✏️ Hábito]   [📅 Citas]
[📋 Semana]   [🏠 Menú]
```

### Hábito multi-día
```
[Lun 30 ✅] [Mar 31 ✅] [Mié 1 ✅]
[Jue 2 ✅]  [Vie 3 ✅]  [Sáb 4 ✅]  [Dom 5 ☐]  ← domingo libre

[📊 Mismo valor para todos]
[✏️ Valor diferente por día]
[✅ Registrar en 6 días]
```

### Vista Semana
```
📋 Semana 30 mar — 5 abr
📅 8 citas  📊 5 días con hábitos  📈 nota media: 7.2

Lun 30  📅2  📊ejercicio✅  sueño:7h
Mar 31  📅1  📊—
Mié 1   📅3  📊ejercicio✅
Jue 2   —    📊sueño:6h
Vie 3   📅1  📊ejercicio✅
Sáb 4   —    —
Dom 5   —    —

[Lun 30][Mar 31][Mié 1][Jue 2]
[Vie 3][Sáb 4][Dom 5]
[◀️ Semana ant.]  [Semana sig. ▶️]
[📅 Esta semana]  [🏠 Menú]
```

### Vista Tracking
```
📈 Tracking — Sáb 28 mar

✅ sueño: 8h
✅ ejercicio: 30min
❌ estudio: —
❌ proyecto: —
✅ THC: 2
❌ tabaco: —
❌ humor: —
❌ agua: —

[✏️ Rellenar vacíos]  [📊 Ver semana]
[🏠 Menú]
```

---

## ⚙️ Config de hábitos — totalmente flexible

Los hábitos son configurables por el usuario:

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `boolean` | Sí/No | ejercicio ✅/❌ |
| `numeric` | Número entero o decimal | tabaco: 3 |
| `time` | Duración | sueño: 8h |
| `text` | Texto libre | humor: bien |
| `scale` | Escala 1-10 | humor: 8 |

Cada hábito puede tener:
- **Unidad** (h, min, L, mg...)
- **Botones rápidos** (ej: `6h,7h,8h,9h`)
- **Valor por defecto**
- **Días activos** (ej: L-V solo, sin fines de semana)

### Onboarding — primer uso
```
👋 Configura tu tracking personal

Elige hábitos de ejemplo o crea los tuyos:

[😴 Sueño]      [🏋️ Ejercicio]
[📚 Estudio]    [💻 Proyecto]
[💧 Agua]       [😄 Humor]
[➕ Añadir el mío]
[✅ Listo, empezar]
```

---

## 🛣️ Roadmap F9.5 — lo que se codifica ahora

1. **Fix bug semana** — `TypeError: can only concatenate list (not tuple)`
2. **Fecha real en nav** — botón central muestra `Sáb 28 mar` real
3. **Saludo contextual** — 🌅/🌆/🌙 según hora + aviso citas hoy
4. **Franjas horarias** — Mañana/Tarde/Noche → hora en punto → cuartos → exacta
5. **➕ Nueva desde vista citas** — sin usar /nueva
6. **✏️ Hábito desde vista hábitos** — directo
7. **Cita multi-día** — toggle semanal + mismo/diferente horario
8. **Hábito multi-día** — toggle semanal + mismo/diferente valor
9. **Semana con resumen** — nº citas + días hábitos + nota media

---

_Documentado: 28 marzo 2026 ~15:18 CET_
