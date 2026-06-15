# Estado de Tareas THDORA
*Actualizado: 15 junio 2026 08:19 CEST*

## COMPLETADO HOY ✅

| Tarea | Bloque | IA | Archivo(s) |
|-------|--------|----|------------|
| Anti-timeout + system prompt + function calling | Bloque 1 | Grok | groq_router.py, nlp.py |
| Memoria persistente | Bloque 2.1 | Mistral | src/api/models/conversation.py, src/api/routers/conversations.py |
| Mood detection silencioso | Bloque 2.2 | Mistral | src/agents/mood_detector.py, src/api/models/mood.py |
| Multiusuario (user_id en endpoints) | Bloque 3 | Mistral | src/api/models/event.py, scripts/migrate_user_id.py |
| Metricas + /stats | Bloque 4 | Mistral | src/agents/metrics.py, src/bot/handlers/stats.py |
| Onboarding ConversationHandler | Tarea 1 | Claude | src/bot/handlers/onboarding.py |
| Scheduler (aviso 30min + resumen) | Tarea 2 | Claude | src/bot/scheduler.py |
| Investigacion competidor Toki | Investigacion | Grok | proyectos/thdora/investigacion/competidores-detalle/toki.md |

## PENDIENTE ❌

| Tarea | Bloque | Descripcion | Prioridad |
|-------|--------|-------------|----------|
| Fix await en nlp.py | Bloque 1.1 | Corregir todos los await en nlp.py | ALTA |
| Integrar onboarding en main.py | Tarea 1.b | Registrar get_onboarding_handler() antes del NLP | ALTA |
| Añadir metodos a api_client.py | Tarea 2.b | get_appointments_today + get_user_name | ALTA |
| Registrar router conversations en FastAPI | Bloque 2.1 | include_router(conversations_router) en api/main.py | ALTA |
| Integrar mood_detector en nlp.py | Bloque 2.2 | create_task cada 5 mensajes | MEDIA |
| Integrar api_client metodos de memoria | Bloque 2.1 | save_message + get_history en nlp.py | MEDIA |
| WhatsApp Adapter | Bloque 3 | Adapter layer Twilio/Meta API | BAJA |
| Test suite | Bloque 5 | Cobertura 80% | BAJA |

## PARA CLAUDE - PROXIMAS TAREAS

### TAREA 3 - Fix await nlp.py
Necesita el contenido actual de src/bot/handlers/nlp.py

### TAREA 4 - Integrar todo en main.py
Actualizar src/bot/main.py + src/bot/api_client.py con todos los metodos nuevos

### TAREA 5 - WhatsApp Adapter
Arquitectura completa del adapter layer
