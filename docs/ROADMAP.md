# 🗺️ ROADMAP THDORA

> Última actualización: 27 mayo 2026 (S19)  
> Versión actual: **v0.16.3**  
> Estado: Bot vivo — bloqueado por GROQ_API_KEY expirada

---

## ✅ Completado hasta v0.16.3

| Feature | Versión | Descripción |
|---------|---------|-------------|
| Bot Telegram base | v0.1 | python-telegram-bot v20, handlers básicos |
| API FastAPI | v0.5 | ~14 endpoints REST, SQLAlchemy ORM |
| BBDD SQLite | v0.5 | 4 tablas: appointments, habits, habit_config, user_config |
| NLP Groq | v0.8 | groq_client.py + intent_parser.py, texto libre |
| /nueva citas | v0.10 | Flujo completo con franja horaria + emojis |
| /citas | v0.11 | Lista, navegación ◀️▶️, borrado con confirmación |
| /habitos | v0.12 | Registro diario, botones rápidos |
| /config (F12) | v0.14 | Notificaciones, resumen diario, resumen nocturno |
| APScheduler | v0.14 | Scheduler integrado, avisos de cita |
| /semana | v0.15 | Vista 7 días |
| Confirmación borrado | v0.16 | Muestra nombre+hora antes de eliminar cita |
| Docker + CI | v0.16 | docker-compose, GitHub Actions |
| Documentación base | v0.16 | ARCHITECTURE.md, API_REFERENCE.md, CONVENCIONES.md |

---

## 🚀 S20 — Reactivación (hoy)

> **Objetivo:** Bot respondiendo al 100% en ≤1 hora

| Paso | Tarea | Tiempo est. |
|------|-------|-------------|
| 1 | Renovar `GROQ_API_KEY` → `.env` → `docker compose restart bot` | 5 min |
| 2 | DBeaver → limpiar cita `id:4` (`time = NULL`) | 10 min |
| 3 | Checklist manual completo del bot | 30 min |
| 4 | Abrir issues en GitHub por cada fallo | 10 min |

**Bloqueador único:** `GROQ_API_KEY` expirada. Todo lo demás está OK.

---

## 🔧 S21 — Cimientos (próxima sesión)

> **Objetivo:** Migraciones controladas + limpieza legacy

| Prioridad | Tarea | Motivo |
|-----------|-------|--------|
| 🔴 Alta | **Alembic init** — `src/db/migrations/` está vacío | Desbloquea todos los cambios de esquema futuros |
| 🔴 Alta | **Primera migration** — estado actual del esquema como baseline | Sin esto, multi-usuario y Postgres son imposibles |
| 🟡 Media | Auditar `src/core/` legacy — decidir borrar o mantener | No estorba pero genera ruido mental |
| 🟡 Media | Marcar `src/core/` como `# LEGACY` en `__init__.py` | Claridad para futuros colaboradores |

---

## 🤖 S22 — NLP nativo (Tool Calling)

> **Objetivo:** Groq Tool Calling nativo sin LangChain

| Tarea | Detalle |
|-------|--------|
| Migrar `intent_parser.py` | Cambiar prompt JSON → `tools=[]` en la llamada a Groq |
| Actualizar `groq_client.py` | Pasar `tools` y `tool_choice` al SDK |
| Tests unitarios NLP | Mockear respuestas con Tool Calling |
| Docstrings `groq_router.py` | 26 KB — el archivo más grande del proyecto |

**Nota:** `src/ai/` ya tiene la separación correcta. Solo modificar, no reestructurar.

---

## 📝 S23 — Calidad de código

> **Objetivo:** Deuda técnica de documentación

| Tarea | Detalle |
|-------|--------|
| Docstrings `bot/` | 14 archivos sin docstrings completos |
| Limpieza `docs/` | Evaluar borrar `ECOSYSTEM.md`; mover `CLASES_BEGO.md` y `GUIA_BEGO.md` a `docs/archive/` |
| Actualizar `INDEX.md` | Reflejar estructura real tras S21-S22 |

---

## 🧪 S24 — Tests e2e

> **Objetivo:** Cobertura del flujo crítico /nueva

| Tarea | Detalle |
|-------|--------|
| Tests e2e con `AsyncMock` | Simular flujo completo `/nueva` → confirmación → BBDD |
| Tests integración API | FastAPI TestClient en todos los endpoints |
| CI: coverage badge | Añadir `pytest-cov` al workflow de Actions |

---

## 👥 S25 — Multi-usuario + Postgres

> **Objetivo:** Arquitectura lista para más de un usuario

| Tarea | Detalle |
|-------|--------|
| `user_id` como `BigInteger` | IDs de Telegram son `int64` — fix en migration Alembic |
| FK `appointments.user_id` → `user_config.user_id` | Integridad referencial |
| FK `habits.user_id` → `user_config.user_id` | Idem |
| Alembic migration: SQLite → Postgres | Cambiar `DATABASE_URL` en `.env` |
| Docker: añadir servicio `postgres` | `docker-compose.yml` con volumen persistente |

---

## 🌐 S26+ — Expansión multicanal

> **Objetivo:** THDORA más allá de Telegram

| Feature | ID | Descripción |
|---------|----|-------------|
| WhatsApp | F14 | Twilio Sandbox → mismo FastAPI como backend |
| Voz | F15 | Whisper (STT) + Groq (NLP) + TTS respuesta |
| Gamificación XP | F15 | Reglas `xp_rule` ya en `habit_config` — solo falta la lógica |
| Web dashboard | F16 | React/Vue leyendo la API FastAPI |
| OCR tickets | F17 | `src/core/ocr/` vacía — idea pendiente |

---

## 🏗️ Arquitectura objetivo (visión)

```
FastAPI (núcleo lógico — ya existe)
    ├── Bot Telegram (PTB v20)     ← perfeccionar S20-S24 ✅
    ├── WhatsApp (Twilio)          ← S26 F14
    └── Voz (Whisper + Groq)      ← S26 F15

BBDD:
    SQLite (ahora, mono-usuario)  → Postgres (S25, multi-usuario)

NLP:
    Groq JSON prompt (ahora)     → Groq Tool Calling nativo (S22)
```

---

## 📊 Métricas de progreso

| Métrica | Valor actual |
|---------|-------------|
| Tests unitarios | 9 ✅ |
| Endpoints API | ~14 |
| Archivos bot/ | 14+ |
| Archivos con docstrings completos | ~30% |
| Cobertura e2e | 0% (pendiente S24) |
| Usuarios soportados | 1 (mono-usuario) |
| Canales activos | 1 (Telegram) |

---

_Roadmap generado en S19 — actualizar al cierre de cada sesión_
