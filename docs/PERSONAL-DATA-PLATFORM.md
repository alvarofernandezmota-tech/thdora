# 🏗️ Personal Data Platform — Documentación Completa

**Creado:** 27/03/2026 — Sesión Perplexity + Álvaro  
**Actualizado:** 28/03/2026 — Visión plataforma unificada  
**Estado:** F9.4 ✅ done | F9.5 🔜 next | Tracking módulo diseñado  
**Repos implicados:** [`personal`](https://github.com/alvarofernandezmota-tech/personal) + [`thdora`](https://github.com/alvarofernandezmota-tech/thdora)

---

## 🎯 Visión

**THDORA es la única fuente de verdad.**  
Todo lo que hasta ahora vivía en YAMLs manuales, Markdown y tracking personal pasa a vivir aquí — accesible desde el bot Telegram, desde la API REST y desde VS Code directamente.

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

## 📊 Flujo completo

```
┌─────────────────────────────┐
│  Bot Telegram               │  ← entrada principal móvil
│  /citas /habitos /tracking  │
└─────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  FastAPI (thdora)           │  ← única API
│  /appointments /habits      │
│  /tracking /summary         │
└─────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  YAML (fuente de verdad)    │  ← legible en VS Code
│  data/YYYY-MM-DD.yaml       │
└─────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  SQLite (futuro F11+)       │  ← consultas históricas rápidas
│  tabla: daily_records       │
└─────────────────────────────┘
```

---

## 💾 Estructura de datos

### YAML tracking diario

```yaml
fecha: 2026-03-28
dormir_hora: "00:22"
despertar_hora: "09:30"
horas_sueno: 9.1
estudio_m5_horas: 2.0
proyecto_horas: 1.5
aprendizaje_ia_horas: 1.0
ejercicio: true
ejercicio_minutos: 20
thea_horas: 3.0
tabaco: 1
thc: 2
cocaina: false
dias_sin_cocaina: 23
nota: 7.5
notas: "Tarde productiva. Sistema YAML implementado."
```

---

## 🎯 Sistema de puntuación diaria

| Hábito | Puntos | Condición |
|--------|--------|----------|
| Despertar ≤08:00 | +1.5 | despertar_hora ≤ "08:00" |
| Dormir ≤23:00 | +1.5 | dormir_hora ≤ "23:00" |
| Estudio M5 ≥2h | +2.0 | estudio_m5_horas ≥ 2 |
| Estudio M5 ≥1h | +1.0 | estudio_m5_horas ≥ 1 |
| Proyecto ≥1h | +1.0 | proyecto_horas ≥ 1 |
| Ejercicio | +1.5 | ejercicio = true |
| Thea ≥2h | +0.5 | thea_horas ≥ 2 |
| Tabaco = 0 | +1.0 | tabaco = 0 |
| THC = 0 | +0.5 | thc = 0 |
| Cocaína = NO | +0.5 | cocaina = false |
| **MÁXIMO** | **10.5** | → normaliza a 10 |

---

## 🗺️ Roadmap de implementación

| Feature | Descripción | Estado |
|---------|-------------|--------|
| F9.1 | Bot base + API + navegación | ✅ Done |
| F9.2 | ConversationHandlers + edición | ✅ Done |
| F9.3 | UI unificada — Menú, volver, cambio vistas | ✅ Done |
| F9.4 | Horas clicables + vista detalle cita | ✅ Done |
| **F9.5** | **Franjas horarias + cita multi-día + hábito multi-día + fecha real en nav + fix bug semana** | 🔜 Next |
| **F9.6** | **Módulo Tracking — API endpoints + bot formulario guiado** | 🔜 |
| **F9.7** | **Vista semanal unificada (citas + hábitos + tracking juntos)** | 🔜 |
| **F9.8** | **Vista mes — calendario visual** | 🔜 |
| **F9.9** | **Dashboard tracking — tendencias + racha + nota diaria** | 🔜 |
| F10 | Alertas automáticas (scheduler) | 🔜 |
| F11 | Migración YAML personal → API (sync.py) | 🔜 |

---

## 🔗 Referencias

- **Spec sesión 28-mar:** [`docs/sessions/2026-03-28-vision-plataforma.md`](docs/sessions/2026-03-28-vision-plataforma.md)
- **Schema YAML:** [`personal/00_sistema/schemas/daily-schema.yaml`](https://github.com/alvarofernandezmota-tech/personal/blob/main/00_sistema/schemas/daily-schema.yaml)
- **Script análisis:** [`personal/03_analisis/parse_tracking.py`](https://github.com/alvarofernandezmota-tech/personal/blob/main/03_analisis/parse_tracking.py)

---

_Última actualización: 28 marzo 2026 ~15:04 CET_
