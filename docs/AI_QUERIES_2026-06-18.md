# Registro de Consultas a IAs — THDORA · 18 junio 2026

> Este documento registra todas las consultas realizadas a IAs externas durante la sesión de auditoría.
> Objetivo: trazabilidad completa, nada se pierde en el chat.

---

## IAs Utilizadas

| IA | Modelo | Propósito | Resultado |
|----|--------|-----------|----------|
| **Groq/LLaMA** | `llama-3.3-70b-versatile` | Auditorías de capas 1-5 en tiempo real | ✅ Muy útil — detectó 15 de 17 problemas |
| **Claude** (via script) | `claude-sonnet-4-5` | Auditoría profunda con código real | ✅ Fase 1-3 completa, tests generados |
| **Grok/xAI** | `grok-2-1212` | Análisis rápido de flujo NLP y API | ✅ Confirmó BUG-001 y BUG-002 |
| **Mistral** | `mistral-large-latest` | Revisión de dependencias y Docker | ✅ Confirmó problema depends_on circular |

---

## Sesión con Groq — Auditorías por Capas (20:00–22:00)

### Prompt base utilizado en todas las capas:
```
Auditoría CAPA N de THDORA.
Revisa estos archivos [lista] y detecta:
1. Imports problemáticos top-level
2. Singletons que fallan antes de que .env esté cargado
3. Race conditions en Docker cold-start
4. Dependencias faltantes en requirements.txt
Formato: PROBLEMA #N — [CRÍTICO/MEDIO/BAJO] + fix listo para aplicar
```

### Resumen de hallazgos por capa:

**CAPA 1** — `config.py`, `main.py`, `manager.py`  
→ GITHUB_TOKEN obligatorio, makedirs sin exist_ok, _check_api sin retry

**CAPA 2** — `node.py`, `Dockerfile`, `smoke_test.py`  
→ _tools top-level, ffmpeg faltante en runtime, smoke test débil

**CAPA 3** — `registry.py`, `appointments.py`, `habits.py`, `entrypoint-api.sh`  
→ imports lazy faltantes en tools, entrypoint sin protección de init_db

**CAPA 4** — `api_client.py`, `db/base.py`, `nlp_disambig.py`  
→ _API_BASE top-level, mkdir sin PermissionError, api top-level en disambig

**CAPA 5** — Todos los archivos revisados  
→ `metrics.py` con Prometheus Duplicated timeseries en reloads

---

## Sesión con Claude/Grok — Auditoría QA Completa (22:00–22:30)

### Prompt enviado (versión comprimida):
```
Eres un QA Engineer senior especializado en Python, FastAPI, LangGraph, 
python-telegram-bot v21 y Docker.

Tareas:
1. Bugs de Runtime — detecta problemas que solo aparecen al ejecutar
2. Flujo Crítico — simula: "Mañana dentista 10am" → nlp → crear_cita → API → respuesta
3. 5 Tests Pytest — genera tests críticos con pytest + mocks

Archivos analizados: 19 archivos del repo (src/bot/*, src/agents/*, src/api/*, etc.)
```

### Hallazgos confirmados por la IA:

**FASE 1 — Rutas API:** ✅ Todos los endpoints coinciden entre cliente y servidor.  
Único punto ciego: `habit_config.py` router no se descargó correctamente.

**FASE 2 — Flujo simulado:**
- Paso 1: ✅ Mensaje llega a `_route_free_text`
- Paso 2: ✅ Va a `nlp_handler`
- Paso 3: ❌ **BUG-001** — regex no detecta "tengo dentista"
- Paso 4: ⚠️ **BUG-002** — LLM responde texto pero no crea cita en API
- Paso 5: ✅ `/nueva` sí funciona como flujo alternativo

**FASE 3 — Tests generados:**  
Ver `tests/unit/` (pendiente de implementar los 5 tests críticos).

### Tests críticos pendientes:
1. `test_nlp_regex.py` — detección de intención con y sin verbos de acción
2. `test_appointments_api.py` — creación de cita con mock de manager
3. `test_api_client_validation.py` — validación de user_id 0, -1, None
4. `test_appointments_conflict.py` — detección de solapamientos
5. `test_api_health.py` — health check OK y fallido

---

## Conclusiones de la Sesión

1. **Groq fue el más eficiente** para auditorías iterativas en tiempo real.
2. **Claude/Grok fue más preciso** para análisis de flujo completo y generación de tests.
3. **El script `scripts/ai_audit.py`** automatiza el proceso completo para futuras sesiones.
4. **Nada se pierde**: todos los hallazgos están documentados aquí y en `THDORA_AUDIT_2026-06-18.md`.

---

## Próxima Sesión Recomendada

1. Ejecutar `make smoke` y verificar que pasan los 22 checks.
2. Ejecutar `make fresh` y probar `/start`, `hola`, "mañana tengo dentista a las 10", `/citas`.
3. Ejecutar `python scripts/ai_audit.py` con ANTHROPIC_API_KEY o GROK_API_KEY.
4. Revisar `audit_report.md` generado y pasarlo aquí para aplicar los fixes.
5. Implementar los 5 tests pytest críticos.
6. Fix BUG-001 (regex NLP) y BUG-002 (LLM → create_appointment).
