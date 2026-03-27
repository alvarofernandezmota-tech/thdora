# 🏗️ Personal Data Platform — Documentación Completa

**Creado:** 27/03/2026 — Sesión Perplexity + Álvaro  
**Estado:** Diseño completo ✅ | Implementación: F1 hecha, F2-F6 pendientes  
**Repos implicados:** [`personal`](https://github.com/alvarofernandezmota-tech/personal) + [`thdora`](https://github.com/alvarofernandezmota-tech/thdora)

---

## 🎯 Visión

Convertir el sistema de tracking diario manual (Markdown) en un **ecosistema de datos vivo** donde:
- Los datos se escriben en YAML estructurado (rápido, legible, versionado)
- Un script Python los procesa y sincroniza automáticamente
- Una base de datos SQLite permite consultas rápidas e historial largo
- El bot Telegram da acceso inmediato desde el móvil
- Las alertas proactivas ayudan a mantener hábitos sin esfuerzo consciente

---

## 📊 Flujo completo

```
┌─────────────────────────────┐
│  Álvaro escribe YAML        │  ← cada noche ~2 min
│  YYYY-MM-DD.yaml            │
└─────────┬──────────────────┗
           │
           ▼
┌─────────────────────────────┐
│  parse_tracking.py          │  ← repo personal/
│  valida + calcula nota      │  03_analisis/
└─────────┬──────────────────┗
           │
           ▼
┌─────────────────────────────┐
│  SQLite (thdora)            │  ← thdora/datos/
│  tabla: daily_records       │
└─────────┬──────────────────┗
           │
           ▼
┌─────────────────────────────┐
│  thdora FastAPI             │  ← nuevos endpoints
│  GET /tracking/semana/13   │  GET /tracking/mes/3
└─────────┬──────────────────┗
           │
           ▼
┌─────────────────────────────┐
│  Bot Telegram               │  ← acceso móvil
│  /stats /habitos /nota-hoy  │
└─────────┬──────────────────┗
           │
           ▼
┌─────────────────────────────┐
│  Alertas automáticas        │  ← scheduler
│  "3 días sin ejercicio"     │
└─────────────────────────────┘
```

---

## 💾 Estructura de datos

### YAML diario (fuente de verdad — repo `personal`)

```yaml
fecha: 2026-03-27
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

### Tabla SQLite `daily_records` (thdora)

```sql
CREATE TABLE daily_records (
    id              INTEGER PRIMARY KEY,
    fecha           DATE UNIQUE NOT NULL,
    dormir_hora     TEXT,
    despertar_hora  TEXT,
    horas_sueno     REAL,
    estudio_horas   REAL DEFAULT 0,
    proyecto_horas  REAL DEFAULT 0,
    ia_horas        REAL DEFAULT 0,
    ejercicio       BOOLEAN DEFAULT FALSE,
    ejercicio_min   INTEGER DEFAULT 0,
    thea_horas      REAL DEFAULT 0,
    tabaco          INTEGER DEFAULT 0,
    thc             INTEGER DEFAULT 0,
    cocaina         BOOLEAN DEFAULT FALSE,
    dias_sin_coca   INTEGER,
    nota            REAL,
    notas           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎯 Sistema de puntuación diaria

> **Filosofía:** La nota se calcula por criterios objetivos, no por sensación subjetiva.
> El script la calcula automáticamente si se dan los datos del día.

### Fórmula (pendiente de refinar en T19/T20)

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
| **MÁXIMO** | **10.5** | → se normaliza a 10 |

> ⚠️ Esta fórmula está en borrador. Se refina en T19 (S13) antes de implementarla en el script.

### Escala de notas semanales (T20)

| Nota | Significado |
|------|-------------|
| 9-10 | Semana excepcional. Todo en verde. |
| 7-8 | Semana sólida. Metas principales cumplidas. |
| 5-6 | Semana aceptable. Algunas caídas. |
| 3-4 | Semana difícil. Tendencia negativa. |
| 0-2 | Semana crítica. Revisar causas. |

---

## 📅 Plan de implementación por fases

| Fase | Qué | Dónde | Semana |
|------|-----|-------|--------|
| **F1** ✅ | YAML schema + plantilla + YAMLs S13 + `parse_tracking.py` básico | `personal/` | S13 (hoy) |
| **F2** | Definir fórmula nota diaria exacta | `personal/00_sistema/` | S13 sábado |
| **F3** | Script calcula nota automáticamente | `personal/03_analisis/` | S13 domingo |
| **F4** | Modelo SQLAlchemy `DailyRecord` en thdora | `thdora/src/tracking/` | S14 |
| **F5** | `sync.py`: YAML → SQLite | `thdora/src/tracking/` | S14 |
| **F6** | Endpoints FastAPI `/tracking/*` | `thdora/src/api/` | S14 |
| **F7** | Bot: `/stats` `/habitos` `/nota-hoy` `/racha` | `thdora/src/bot/` | S15 |
| **F8** | Alertas automáticas (scheduler) | `thdora/src/scheduler/` | S15-S16 |

---

## 🔗 Referencias

- **Schema YAML:** [`personal/00_sistema/schemas/daily-schema.yaml`](https://github.com/alvarofernandezmota-tech/personal/blob/main/00_sistema/schemas/daily-schema.yaml)
- **Plantilla diaria:** [`personal/00_sistema/schemas/daily-template.yaml`](https://github.com/alvarofernandezmota-tech/personal/blob/main/00_sistema/schemas/daily-template.yaml)
- **Script análisis:** [`personal/03_analisis/parse_tracking.py`](https://github.com/alvarofernandezmota-tech/personal/blob/main/03_analisis/parse_tracking.py)
- **Datos S13:** [`personal/01_traking_diario/data/2026/03/`](https://github.com/alvarofernandezmota-tech/personal/tree/main/01_traking_diario/data/2026/03)
- **ROADMAP thdora:** [ROADMAP.md](ROADMAP.md)

---

_Creado: 27 marzo 2026 17:42 CET — Sesión de planificación Perplexity + Álvaro_  
_Próxima actualización: S13 domingo — fórmula nota diaria refinada_
