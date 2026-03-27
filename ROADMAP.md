# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.7.1 (27 marzo 2026)

```
FastAPI (endpoints CRUD completos)
    ↕ httpx async
ThdoraApiClient (7 métodos + update/delete)
    ↕ python-telegram-bot 22
Bot Telegram (5 comandos + 4 ConversationHandlers + inline buttons)
```

**Lo que funciona hoy:**
- `/start` `/citas` `/habitos` `/habito` `/nueva` `/resumen` `/cancelar`
- Inline buttons: borrar/editar citas y hábitos, acumulación `+N`
- Fechas flexibles: `hoy`, `mañana`, `ayer`, `27/03`, nombres de día
- API: GET/POST/DELETE/PUT para citas y hábitos

---

## 🔴 F7 — Fixes y cierre (próxima sesión)

> Objetivo: dejar F7 sin bugs conocidos y con tests

- [ ] **Fix bug tipo `/nueva`** — el paso 4 (tipo inline) se salta, cita se crea siempre con "otra"
- [ ] **Fix contexto acumulación suelto** — limpiar `acum_hab_nombre` al entrar en `/citas` y `/habitos`
- [ ] **Quitar UUID de mensajes** — solo mostrar índice numérico
- [ ] **Navegación temporal** — botones ◀️ Ayer / ▶️ Mañana en `/citas` y `/habitos`
- [ ] **Tests API nuevos** — `PUT /appointments`, `DELETE/PUT /habits`
- [ ] **`/agenda`** — vista de los próximos 7 días con citas

---

## 🟠 F8 — Endpoints y calendario (después de F7)

> Objetivo: ampliar la API con vistas temporales y mejorar la gestión de calendario

- [ ] `GET /appointments/upcoming` — próximas citas desde hoy (para `/proximas`)
- [ ] `GET /summary/week/{date}` — resumen semanal de hábitos con totales
- [ ] `/resumen` con botón ➕ Nueva cita inline
- [ ] `src/bot/config.py` — centralizar `TELEGRAM_BOT_TOKEN`, `API_URL`, timeouts
- [ ] Comando `/agenda` en bot (7 días, citas agrupadas por día)

---

## 🟡 F9 — Persistencia real (SQLite)

> Objetivo: pasar de JSON a base de datos real

- [ ] `SQLiteLifeManager` implementando `AbstractLifeManager`
- [ ] Migraciones con `alembic`
- [ ] Tests de integración con BD real
- [ ] Mantener `JsonLifeManager` como fallback

---

## 🟢 F10 — IA integrada

> Objetivo: procesamiento de lenguaje natural para crear citas y registrar hábitos

- [ ] Groq API para comandos de texto libre: "mañana a las 10 tengo médico"
- [ ] Ollama local para análisis de datos personales
- [ ] Comando `/ia` — modo conversación libre
- [ ] Sugerencias automáticas de hábitos basadas en patrones

---

## ⚪ F11 — Dashboard web

> Objetivo: interfaz visual para el historial

- [ ] FastAPI con Jinja2 o React frontend
- [ ] Gráficas de hábitos (Chart.js)
- [ ] Exportar datos a CSV/JSON

---

## ⚪ F12 — Despliegue

> Objetivo: THDORA corriendo 24/7

- [ ] Docker Compose: `api` + `bot` + volumen de datos
- [ ] VPS o Raspberry Pi local
- [ ] Variables de entorno con `python-dotenv` en producción
- [ ] Health checks y reinicio automático

---

_Última actualización: 27 marzo 2026 — 21:40 CET_
