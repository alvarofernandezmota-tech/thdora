# Estado de Tareas THDORA
*Actualizado: 15 junio 2026 08:26 CEST*

## COMPLETADO HOY ✅

| Tarea | Bloque | IA | Archivo(s) | Commit |
|-------|--------|----|------------|--------|
| Anti-timeout + system prompt + function calling | Bloque 1 | Grok | groq_router.py, nlp.py | eaa818a |
| Memoria persistente | Bloque 2.1 | Mistral | src/api/models/conversation.py, src/api/routers/conversations.py | a37cbf5 |
| Mood detection silencioso | Bloque 2.2 | Mistral | src/agents/mood_detector.py, src/api/models/mood.py | a37cbf5 |
| Multiusuario (user_id en endpoints) | Bloque 3 | Mistral | src/api/models/event.py, scripts/migrate_user_id.py | a37cbf5 |
| Metricas + /stats | Bloque 4 | Mistral | src/agents/metrics.py, src/bot/handlers/stats.py | a37cbf5 |
| Onboarding ConversationHandler | Tarea 1 | Claude | src/bot/handlers/onboarding.py | a37cbf5 |
| Scheduler (aviso 30min + resumen matutino) | Tarea 2 | Claude | src/bot/scheduler.py | a37cbf5 |
| Fix await nlp.py + mood integrado + historial BD | Tarea 3 | Claude | src/bot/handlers/nlp.py | este commit |
| api_client.py completo (ThdoraApiClient) | Tarea 5 | Claude | src/bot/api_client.py | este commit |
| Investigacion competidor Toki | Investigacion | Grok | proyectos/thdora/investigacion/competidores-detalle/toki.md | a37cbf5 |

## PENDIENTE ❌

| Tarea | Descripcion | Prioridad | Para quien |
|-------|-------------|----------|------------|
| main.py v4.4 | Integrar onboarding + /stats en main.py real (no sobreescribir el existente) | ALTA | Claude |
| groq_router.py | Añadir parametro extra_context a process_message() | ALTA | Claude |
| WhatsApp Adapter | Adapter layer Twilio/Meta API + webhook | MEDIA | Claude |
| Documentacion completa | Gemini documenta todos los archivos nuevos | MEDIA | Gemini |
| Reestructuracion | Revision arquitectura general + optimizacion | BAJA | Claude |
| Test suite | Cobertura 80% | BAJA | Claude |

## ROADMAP PROGRESO

```
Bloque 1 — NLP core          ████████████████████ 100% ✅
Bloque 2 — Memoria + Mood    ████████████████░░░░  80% 🟡 (falta groq_router extra_context)
Bloque 3 — Multiusuario      ████████████████░░░░  80% 🟡 (falta main.py v4.4)
Bloque 4 — Metricas          ████████████████░░░░  80% 🟡 (falta /stats en main.py)
Bloque 5 — WhatsApp          ░░░░░░░░░░░░░░░░░░░░   0% ❌
Bloque 6 — Tests             ░░░░░░░░░░░░░░░░░░░░   0% ❌
```

**Progreso global: ~75%**
