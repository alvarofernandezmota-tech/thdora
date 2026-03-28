# 🏗️ Personal Data Platform — Documentación Completa

**Creado:** 27/03/2026 — Sesión Perplexity + Álvaro  
**Actualizado:** 28/03/2026 21:43 CET  
**Repos implicados:** [`personal`](https://github.com/alvarofernandezmota-tech/personal) + [`thdora`](https://github.com/alvarofernandezmota-tech/thdora)

---

## 🎯 Visión

**THDORA es la única fuente de verdad.**  
Todo lo que hasta ahora vivía en YAMLs manuales, Markdown y tracking personal pasa a vivir aquí — accesible desde el bot Telegram, desde la API REST y desde VS Code directamente.

```
FastAPI (backend)
    │
    ├── 📅 Citas         →  SQLite (data/thdora.db)
    ├── 📊 Hábitos       →  SQLite (data/thdora.db)
    ├── 📈 Tracking      →  SQLite (futuro F10)
    └── 📋 Diarios       →  docs/diarios/YYYY-MM-DD.md
         │
         ├── Bot Telegram   →  móvil (Álvaro)
         ├── API REST        →  Claude / Perplexity / scripts
         └── YAML / MD       →  VS Code (lectura directa)
```

---

## 🗺️ Roadmap de implementación

| Feature | Descripción | Estado |
|---------|-------------|--------|
| F9.1 | Bot base + API + SQLite | ✅ Done |
| F9.2 | Fixes ConversationHandlers | ✅ Done |
| F9.3 | UI unificada — Menú, volver, cambio vistas | ✅ Done |
| F9.4 | Horas clicables + vista detalle cita | ✅ Done |
| F9.5 | UX avanzada — fecha real nav + saludo + hábito libre | ✅ Done |
| **F9.6** | **Refactor handlers.py en módulos** | 🔜 Next |
| **F9.7** | **Docker + despliegue 24/7** | 🔜 |
| **F9.8** | **Multi-usuario (user_id)** | 🔜 |
| **F10** | **Módulo Tracking personal** | 🔜 |
| **F11** | **Notificaciones APScheduler** | 🔜 |
| **F12** | **IA conversacional (Groq/OpenAI/Claude)** | 🔜 |
| **F13** | **Gamificación RPG** | 🔜 |
| **F14** | **Telegram Mini App (React)** | 🔜 |
| **F15** | **PWA instalable** | 🔜 |
| **F16** | **React Native (si escala)** | 🔜 |

---

## 💾 Estructura de datos actual

### SQLite — tablas activas
```
data/thdora.db
├── appointments  → id, date, time, name, type, notes
├── habits        → id, date, name, value
└── habit_config  → id, name, habit_type, unit, quick_vals
```

### YAML tracking diario (F10 — pendiente)
```yaml
fecha: 2026-03-28
dormir_hora: "00:22"
despertar_hora: "09:30"
horas_sueno: 9.1
estudio_horas: 2.0
proyecto_horas: 1.5
ejercicio: true
ejercicio_minutos: 20
nota: 7.5
notas: "Tarde productiva."
```

---

## 🎯 Sistema de puntuación diaria (F10)

| Hábito | Puntos | Condición |
|--------|--------|----------|
| Despertar ≤08:00 | +1.5 | despertar_hora ≤ "08:00" |
| Dormir ≤23:00 | +1.5 | dormir_hora ≤ "23:00" |
| Estudio ≥2h | +2.0 | estudio_horas ≥ 2 |
| Proyecto ≥1h | +1.0 | proyecto_horas ≥ 1 |
| Ejercicio | +1.5 | ejercicio = true |
| Tabaco = 0 | +1.0 | tabaco = 0 |
| THC = 0 | +0.5 | thc = 0 |
| **MÁXIMO** | **10.5** | → normaliza a 10 |

---

## 🔗 Referencias

- **ROADMAP:** [`ROADMAP.md`](../ROADMAP.md)
- **CHANGELOG:** [`CHANGELOG.md`](../CHANGELOG.md)
- **Sesión 28-mar auditoría:** [`sessions/2026-03-28-session-auditoria.md`](sessions/2026-03-28-session-auditoria.md)
- **Sesión 28-mar visión:** [`sessions/2026-03-28-vision-plataforma.md`](sessions/2026-03-28-vision-plataforma.md)

---

_Última actualización: 28 marzo 2026 — 21:43 CET_
