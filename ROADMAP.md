# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.8.0 (27 marzo 2026)

```
Bot Telegram (7 comandos + 4 ConversationHandlers + inline buttons)
    ↕ httpx async
ThdoraApiClient (9 métodos)
    ↕ FastAPI REST
API (14 endpoints: CRUD + semana + rango + stats)
    ↕ SQLAlchemy ORM
SQLite (data/thdora.db — persistencia real)
```

**Lo que funciona hoy:**
- `/start` `/citas` `/habitos` `/habito` `/nueva` `/resumen` `/cancelar`
- Inline buttons: borrar/editar citas y hábitos, acumulación `+N`
- Fechas flexibles: `hoy`, `mañana`, `ayer`, `27/03`, nombres de día
- API: 14 endpoints — CRUD + rango + semana + stats + upcoming
- **Datos persistentes en SQLite** — sobreviven a reinicios

---

## ✅ Completadas

### F1–F5 — Base, abstracción, core
- `AbstractLifeManager`, `MemoryLifeManager`, `JsonLifeManager`
- Arquitectura limpia con ADRs

### F6 — FastAPI REST
- Endpoints CRUD para citas y hábitos
- `GET /summary/{date}`

### F7 — Bot Telegram v2
- 5 comandos + `/nueva` 5 pasos + inline buttons
- Fechas flexibles con `dateparser`
- Acumulación `+N` en hábitos
- Fix bug tipo `/nueva` (v2.1)
- Fix contexto acum suelto (v2.1)

### F8 — Endpoints temporales
- `GET /appointments/week/{date}` — citas de la semana
- `GET /appointments/range/{from}/{to}` — citas en rango
- `GET /appointments/upcoming/{date}` — próximas citas
- `GET /habits/week/{date}` — hábitos de la semana
- `GET /habits/range/{from}/{to}` — hábitos en rango
- `GET /habits/stats/{habit}?days=N` — historial hábito
- `GET /summary/week/{date}` — resumen semanal

### F9 — Persistencia SQLite ✅
- `src/db/base.py` — SQLAlchemy engine + `get_session()` + `init_db()`
- `src/db/models.py` — tablas `appointments` + `habits`
- `SQLiteLifeManager` — CRUD completo + rangos + upsert
- Routers migrados: ya no usan `JsonLifeManager`
- `data/thdora.db` — archivo SQLite local

---

## 🔶 F10 — Gamificación RPG (próxima)

> **Objetivo:** convertir el tracking de hábitos en un videojuego

### Sistema de XP y niveles

| Hábito | Condición | XP |
|--------|-----------|----|
| sueño | ≥ 7h | +20 XP |
| ejercicio | cualquier valor | +30 XP |
| estudio | cualquier valor | +40 XP |
| agua | ≥ 2L | +15 XP |
| humor | ≥ 7 | +10 XP |
| sin sustancias | valor = 0 | +50 XP |
| racha 7 días | todos los hábitos | +200 XP bonus |

**Niveles:**
```
0      XP → Novato
500    XP → Aprendiz
1500   XP → Guerrero
3500   XP → Maestro
7500   XP → Leyenda
```

### Tareas F10
- [ ] `src/db/models.py` — nueva tabla `player_stats` (xp, level, streak, last_update)
- [ ] `src/core/rpg/xp_engine.py` — cálculo de XP por hábito
- [ ] `src/core/rpg/level_system.py` — niveles y umbrales
- [ ] `src/core/rpg/streak_tracker.py` — rachas diarias
- [ ] `src/api/routers/rpg.py` — endpoints: `GET /rpg/stats`, `POST /rpg/process/{date}`
- [ ] `src/bot/handlers.py` — `/stats` — ver nivel, XP, racha actual
- [ ] `/resumen` muestra XP ganado del día + nivel actual
- [ ] Notificación automática al subir de nivel
- [ ] Misiones diarias: "Registra 5 hábitos hoy" → bonus XP
- [ ] Tests del motor RPG

---

## ⚪ F11 — IA local (Groq / Ollama)

> **Objetivo:** procesamiento de lenguaje natural y análisis de patrones

- [ ] Groq API para comandos de texto libre: "mañana a las 10 tengo médico"
- [ ] Ollama local para análisis de datos personales
- [ ] Comando `/ia` — modo conversación libre
- [ ] Sugerencias automáticas basadas en patrones de hábitos
- [ ] Análisis semanal: "Esta semana dormiste menos que la anterior"

---

## ⚪ F12 — Dashboard web

> **Objetivo:** interfaz visual para el historial

- [ ] FastAPI + Jinja2 o React
- [ ] Gráficas de hábitos por semana/mes
- [ ] Barra de XP y nivel RPG
- [ ] Exportar datos a CSV/JSON

---

## ⚪ F13 — Despliegue

> **Objetivo:** THDORA corriendo 24/7

- [ ] Docker Compose: `api` + `bot` + volumen `data/`
- [ ] VPS o Raspberry Pi
- [ ] Health checks y reinicio automático
- [ ] Backup automático de `thdora.db`

---

_Última actualización: 27 marzo 2026 — 22:21 CET_
