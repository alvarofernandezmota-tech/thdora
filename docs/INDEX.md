# 📖 THDORA — Índice de documentación

> **Navegación:** [README](../README.md) · [CHANGELOG](../CHANGELOG.md) · [ROADMAP](../ROADMAP.md)

**Versión:** v0.8.0 — **Última actualización:** 27 marzo 2026

---

## 🏗️ Arquitectura

| Documento | Descripción |
|-----------|-------------|
| [ARCHITECTURE.md](architecture/ARCHITECTURE.md) | Visión general del sistema |
| [ADR-001](architecture/ADR-001-abstract-lifemanager.md) | AbstractLifeManager |
| [ADR-002](architecture/ADR-002-json-storage.md) | Almacenamiento JSON |
| [ADR-003](architecture/ADR-003-fastapi.md) | FastAPI como API REST |
| [ADR-004](architecture/ADR-004-telegram-bot.md) | Bot Telegram |

---

## 🧩 Módulos

| Módulo | Ruta | Descripción |
|--------|------|-------------|
| API | `src/api/` | FastAPI: 14 endpoints CRUD + semana + rango + stats |
| Bot | `src/bot/` | Telegram: 7 comandos + inline buttons |
| Core | `src/core/` | Abstracción + SQLiteLifeManager + JsonLifeManager |
| DB | `src/db/` | SQLAlchemy ORM + modelos + engine |
| AI | `src/ai/` | Pendiente F11 |

### Documentación por módulo

- [Módulo DB](modules/db.md) — SQLite, modelos, SQLiteLifeManager
- [Módulo Bot](modules/bot.md) — handlers, comandos, ConversationHandlers

---

## 🗒️ Diarios de sesión

| Fecha | Resumen |
|-------|---------|
| [2026-03-27](diarios/2026-03-27.md) | F7 bot v2, F9 SQLite, F9.1 routers, fixes |
| [2026-03-24](diarios/2026-03-24.md) | F1–F6: base, core, API REST |

---

## 🔎 Auditorías

| Repo | Documento |
|------|-----------|
| thea-ia | [auditoría](auditoria/thea-ia.md) |

---

## 🎮 Plan RPG (F10)

### XP por hábito

| Hábito | Condición | XP |
|--------|-----------|----|
| sueño | ≥ 7h | +20 |
| ejercicio | registrado | +30 |
| estudio | registrado | +40 |
| agua | ≥ 2L | +15 |
| humor | ≥ 7 | +10 |
| sustancias | = 0 | +50 |
| racha 7d | completa | +200 bonus |

### Niveles

| XP | Nivel |
|----|-------|
| 0 | 🦣 Novato |
| 500 | 📘 Aprendiz |
| 1500 | ⚔️ Guerrero |
| 3500 | 🌟 Maestro |
| 7500 | 🔥 Leyenda |

---

_Última actualización: 27 marzo 2026 — 22:21 CET_
