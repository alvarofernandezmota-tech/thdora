# 📚 Índice de documentación — THDORA

> Última actualización: 27 mayo 2026 (S19 — auditoría completa)  
> Versión: **v0.16.3**

---

## 🗺️ Navegación rápida

| Documento | Descripción | Estado |
|-----------|-------------|--------|
| **[ROADMAP.md](./ROADMAP.md)** | Roadmap completo S20→S26+ con tareas por sesión | ✅ Actualizado S19 |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | Arquitectura del sistema, capas, flujo de datos | ✅ Vigente |
| **[API_REFERENCE.md](./API_REFERENCE.md)** | Endpoints FastAPI documentados | ✅ Vigente |
| **[CONVENCIONES.md](./CONVENCIONES.md)** | Convenciones de código, naming, commits | ✅ Vigente |
| **[GIT_GUIDE.md](./GIT_GUIDE.md)** | Flujo de ramas, commits semánticos, PRs | ✅ Vigente |
| **[NLP_ARQUITECTURA.md](./NLP_ARQUITECTURA.md)** | Diseño del sistema NLP (Groq + intent parser) | ✅ Vigente |
| **[FLUJOS_DETALLADOS.md](./FLUJOS_DETALLADOS.md)** | Flujos de conversación del bot paso a paso | ✅ Vigente |
| **[F12_NOTIFICACIONES_DESIGN.md](./F12_NOTIFICACIONES_DESIGN.md)** | Diseño del sistema de notificaciones | ✅ Vigente |
| **[PERSONAL-DATA-PLATFORM.md](./PERSONAL-DATA-PLATFORM.md)** | Visión de plataforma de datos personales | ✅ Vigente |
| **[INTEGRACION_TICKET_PARSER.md](./INTEGRACION_TICKET_PARSER.md)** | Integración futura de parser de tickets | 📋 Pendiente |
| **[ECOSYSTEM.md](./ECOSYSTEM.md)** | Ecosistema general del proyecto | ⚠️ Revisar S23 |
| **[CLASES_BEGO.md](./CLASES_BEGO.md)** | Notas de clases de programación | ⚠️ Mover a archive/ en S23 |
| **[GUIA_BEGO.md](./GUIA_BEGO.md)** | Guía de onboarding | ⚠️ Mover a archive/ en S23 |

---

## 📂 Estructura de carpetas en docs/

```
docs/
├── INDEX.md                     ← este archivo
├── ROADMAP.md                   ← roadmap S20→S26+  ← NUEVO S19
├── ARCHITECTURE.md              ← arquitectura del sistema
├── API_REFERENCE.md             ← endpoints FastAPI
├── CONVENCIONES.md              ← convenciones de código
├── GIT_GUIDE.md                 ← flujo git
├── NLP_ARQUITECTURA.md          ← sistema NLP
├── FLUJOS_DETALLADOS.md         ← flujos bot
├── F12_NOTIFICACIONES_DESIGN.md ← diseño notificaciones
├── PERSONAL-DATA-PLATFORM.md   ← visión plataforma
├── INTEGRACION_TICKET_PARSER.md ← parser tickets (futuro)
├── ECOSYSTEM.md                 ← ⚠️ revisar S23
├── CLASES_BEGO.md               ← ⚠️ mover a archive/ en S23
├── GUIA_BEGO.md                 ← ⚠️ mover a archive/ en S23
├── diarios/                     ← diario de desarrollo por sesión
│   └── 2026-05-27.md            ← S19 (auditoría completa)
├── sessions/                    ← resúmenes de sesión formales
├── auditoria/                   ← auditorías técnicas
├── architecture/                ← diagramas de arquitectura
├── modules/                     ← documentación por módulo
└── setup/                       ← guías de instalación
```

---

## 🧠 Estado del proyecto (S19 — 27 mayo 2026)

### Veredicto de la auditoría

> **El bot está bien. Lleva 28 días dormido por una sola causa: `GROQ_API_KEY` expirada.**

| Componente | Estado | Notas |
|-----------|--------|-------|
| Bot Telegram | ⚠️ Sin verificar | 28 días sin arrancar |
| API FastAPI | ⚠️ Sin verificar | ~14 endpoints |
| NLP / Groq | 🔴 Bloqueado | Key expirada |
| BBDD SQLite | 🔴 Bomba silenciosa | Cita `id:4` con `time=NULL` |
| Tests unitarios | ✅ 9 tests | Pasando |
| Docker / CI | ✅ OK | Actions pasando |
| `src/core/` | ⚠️ Legacy v1 | No conectado, no estorba |
| `src/ai/` | ✅ Limpio | Listo para Tool Calling |

### Decisiones tomadas en S19

- `cb_hab_add_value` → **no es un bug**, diseño correcto
- Bug #10 `/config` timeout → **ya corregido** en S18
- `src/core/` → **mantener** como legacy hasta S21
- S21: **Alembic primero** (desbloquea todo), luego docstrings
- `src/ai/` → no reestructurar, solo modificar `intent_parser.py` para Tool Calling

---

## ⚡ Arranque rápido (S20)

```bash
# 1. Groq key nueva
cd ~/thdora && nano .env   # GROQ_API_KEY=gsk_nueva
docker compose restart bot
docker compose logs -f bot

# 2. Limpiar BBDD
# DBeaver → DELETE FROM appointments WHERE id = 4;

# 3. Verificar
curl http://localhost:8000/health
```

---

_Índice mantenido manualmente — actualizar al añadir/mover documentos_
