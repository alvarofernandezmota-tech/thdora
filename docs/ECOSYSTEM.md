# 🌐 Ecosistema Álvaro — Mapa Completo

**Creado:** 27/03/2026  
**Estado:** Vivo — actualizar cuando cambie la arquitectura

---

## 🧠 Visión general

Tres repos que forman un ecosistema coherente. Cada uno tiene un rol único y no se solapan. La regla más importante: **los datos personales nunca salen de `personal`**.

---

## 📊 Mapa de repos

```
┌─────────────────────────────────────────────┐
│              personal/                         │
│  • YAMLs diarios (fuente de verdad)           │
│  • Diarios Markdown (narrativa)               │
│  • Semanas, guías, planificación              │
│  • Scripts de análisis local                  │
│  • Formación MUSK (notebooks, PDFs)           │
│                                                │
│  🔒 PRIVADO — datos sensibles aquí siempre    │
└────────────────────┬────────────────────────┗
                     │ lee YAMLs (código, no datos)
                     ▼
┌─────────────────────────────────────────────┐
│              thdora/                           │
│  • Motor técnico del ecosistema               │
│  • FastAPI REST (7 endpoints activos)         │
│  • SQLite → datos estructurados (F11+)        │
│  • Bot Telegram (F7)                          │
│  • Sync YAML → BD (F12)                       │
│  • Alertas automáticas (F13)                  │
│                                                │
│  🔓 PÚBLICO — solo código, nunca datos raw    │
└────────────────────┬────────────────────────┗
                     │ hereda código (NLP, Telegram)
                     ▼
┌─────────────────────────────────────────────┐
│              thea-ia/                          │
│  • Predecesor de thdora (inactivo)            │
│  • Cantera de código reutilizable             │
│  • NLP engine → thdora F8                     │
│  • Telegram adapter → thdora F7               │
│  • Ollama client → thdora F8                  │
│                                                │
│  📜 Archivar tras migrar el código útil        │
└─────────────────────────────────────────────┘
```

---

## 🔄 Flujo de datos completo

```
Álvaro rellena YAML cada noche
  └→ personal/01_traking_diario/data/YYYY/MM/YYYY-MM-DD.yaml

Script local (personal/03_analisis/parse_tracking.py)
  └→ lee YAMLs, calcula métricas, imprime resumen
  └→ uso: python 03_analisis/parse_tracking.py --semana 13

[FUTURO F12 — S14] thdora sync.py
  └→ lee YAMLs vía ruta local o GitHub API
  └→ valida schema, inserta en SQLite (tabla daily_records)

[FUTURO F12] thdora FastAPI nuevos endpoints
  └→ GET /tracking/semana/13
  └→ GET /tracking/mes/3
  └→ GET /tracking/nota-hoy

[FUTURO F13 — S15] thdora Bot Telegram
  └→ /stats — resumen semanal
  └→ /habitos — estado hábitos semana actual
  └→ /nota-hoy — nota calculada del día
  └→ /racha — rachas activas
  └→ alertas: "3 días sin ejercicio ⚠️"
```

---

## 🛠️ Código que viaja de thea-ia a thdora

| Módulo | Origen | Destino | Fase |
|--------|--------|---------|------|
| Telegram adapter | `thea-ia/src/theaia/adapters/telegram/` | `thdora/src/bot/` | F7 |
| NLP engine (intención por regex) | `thea-ia/src/theaia/core/nlp_engine.py` | `thdora/src/ai/` | F8 |
| Ollama client | `thea-ia/src/theaia/adapters/ollama/` | `thdora/src/ai/` | F8 |

> ⚠️ No copiar — adaptar. thea-ia tiene deuda técnica. Tomar la lógica, no el código literalmente.

---

## 🚧 Reglas de privacidad — NO negociables

1. **Los archivos `.yaml` de tracking NUNCA van a `thdora`** ni a ningún repo público.
2. **Los diarios `.md` de `personal` NUNCA van a `thdora`.**
3. **thdora solo tiene código** — el sync lee desde una ruta local o GitHub API con token privado.
4. **`personal` debe volverse privado** — pendiente (auditado en S13).

---

## 📋 Estado actual por repo

| Repo | Versión | Estado | Fase activa |
|------|---------|--------|-------------|
| `personal` | — | ✅ Activo | Sistema YAML + análisis |
| `thdora` | v0.6.1 | ✅ Activo | F7 Bot Telegram (S14) |
| `thea-ia` | — | 💤 Inactivo | Cantera → archivar en F9 |

---

## 📅 Hoja de ruta del ecosistema

| Semana | Hito |
|--------|------|
| S13 (ahora) | Sistema YAML activo, script análisis, PDP documentado |
| S14 | thdora F7 Bot Telegram + F12 sync YAML→SQLite |
| S15 | thdora F13 /stats /habitos /nota-hoy + alertas |
| S16 | thdora F8 Ollama + NLP desde thea-ia |
| S17+ | thea-ia archivado oficialmente |

---

## 🔗 Referencias cruzadas

- **Guía semanal sistema:** [personal/00_sistema/GUIA-SEMANAL-SISTEMA.md](https://github.com/alvarofernandezmota-tech/personal/blob/main/00_sistema/GUIA-SEMANAL-SISTEMA.md)
- **PDP arquitectura:** [thdora/docs/PERSONAL-DATA-PLATFORM.md](./PERSONAL-DATA-PLATFORM.md)
- **ROADMAP thdora:** [thdora/ROADMAP.md](../ROADMAP.md)
- **Schema YAML:** [personal/00_sistema/schemas/daily-schema.yaml](https://github.com/alvarofernandezmota-tech/personal/blob/main/00_sistema/schemas/daily-schema.yaml)
- **thea-ia (cantera):** [github.com/alvarofernandezmota-tech/thea-ia](https://github.com/alvarofernandezmota-tech/thea-ia)

---

_Creado: 27 marzo 2026 17:50 CET_  
_Próxima actualización: cuando cambie la arquitectura o se complete una fase_
