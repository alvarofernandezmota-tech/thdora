# 🔬 THDORA — Research & Architecture Decisions

> Investigaciones realizadas con Gemini — 17 jun 2026  
> Alimentan Sprint 5 (implementación inmediata) y Sprint 6 (arquitectura thdora-base)

---

## INV-1 — Ollama Nivel 1: qwen2.5:3b vs gemma3:4b

### ✅ Decisión: `qwen2.5:3b-instruct-q4_K_M`

**Qwen2.5:3b es el ganador claro para el Nivel 1 de THDORA.**

| Métrica | qwen2.5:3b (Q4_K_M) | gemma3:4b |
|---|---|---|
| RAM consumida | **~2.2 GB** | ~3.5 GB |
| TTFT en CPU consumer | **40–60ms** | ~120–200ms |
| Español corto (NLU) | ✅ Superior | ⚠️ Regular |
| JSON/Tool Calling | ✅ Nativo | ⚠️ Inestable en 4B |

**Argumentos clave:**
- Preentrenamiento multilingüe de Qwen2.5 supera a Gemma en NLU de baja densidad de tokens en español
- Entrenado explícitamente para outputs estructurados (JSON) con System Prompt agresivo
- temperature=0.0 + schema JSON estricto → clasificaciones estables <150ms

**Configuración en Madre:**
```bash
ollama pull qwen2.5:3b-instruct
```
```python
# llm_factory.py — nivel 1
OLLAMA_MODEL_LEVEL1 = "qwen2.5:3b-instruct"
# System prompt nivel 1:
# Devuelve SOLO JSON: {"intent": "...", "confidence": 0.0}
```

---

## INV-2 — Compresión de historial sin perder contexto emocional

### ✅ Decisión: Dual-Layer Summarization + `user_emotional_state`

**Técnica: Memoria Episódica con Etiquetado de Metadatos Emocionales.**

| Técnica | Veredicto |
|---|---|
| Truncación simple | ❌ Elimina contexto emocional completamente |
| Resumen LLM estándar | ⚠️ "Limpia" el texto eliminando tono y frustración |
| Embeddings semánticos | ⚠️ Pierde línea temporal y evolución del estado |
| **Dual-Layer (ganador)** | ✅ Separa hechos duros de perfil afectivo |

**Pipeline (cuando `nlp_history` supera 15 mensajes):**

1. Llamada async a Groq con los mensajes a comprimir
2. Prompt obliga a devolver:
```json
{
  "facts_extracted": ["Cita con el médico el jueves a las 17:00"],
  "affective_context": "El usuario muestra ansiedad por los resultados; requiere respuestas directas y tono empático."
}
```
3. `facts_extracted` → SQLite (tabla existente)
4. `affective_context` → tabla nueva `user_emotional_state` en SQLite
5. Inyectar `affective_context` como directiva dinámica en el System Prompt de Groq

**Implementación prevista:** Sprint 6 — `src/agents/memory/emotional_compressor.py`

---

## INV-3 — Arquitectura thdora-base (Sprint 6)

### ✅ Decisión: Composición + Sistema de Hooks/Middlewares

**Patrón: `ThdoraEngine` como núcleo agnóstico al transporte.**

```
[Telegram / Cliente]  ──>  ( ThdoraEngine )
                                │
                                ├──> 1. Pre-routing Hooks (Regex nivel 0)
                                ├──> 2. Intent Routing (Ollama/Qwen nivel 1)
                                └──> 3. Execution & Post-LLM Hooks (Groq nivel 2)
```

**Firma de diseño:**
```python
# thdora_base/engine.py
class ThdoraEngine:
    def __init__(self, router_config, llm_factory):
        self.router = router_config
        self.llm = llm_factory
        self._pre_hooks = []

    def register_pre_hook(self, func):
        self._pre_hooks.append(func)

    async def process_message(self, user_id: str, text: str) -> AgentResponse:
        # Lógica 3 niveles: Regex -> Ollama -> Groq
        ...
```

**Por qué no herencia:**
- Herencia acopla lógica de negocio al framework de Telegram
- Imposible hacer unit tests del LLM sin levantar el bot
- Bloquea migración futura a Discord / WebUI

**Referencias:** LangGraph, FastAPI Dependencies, aiogram 3.x middlewares, patrón Chain of Responsibility.

**Estructura prevista Sprint 6:**
```
thdora_base/
├── engine.py          ← ThdoraEngine
├── hooks.py           ← registro de pre/post hooks
├── intent_router.py   ← 3 niveles
├── llm_factory.py     ← migrado desde src/bot/
└── models.py          ← AgentResponse, IntentResult
```

---

## INV-4 — Memoria semántica: sqlite-vec vs ChromaDB vs pgvector

### ✅ Decisión: `sqlite-vec` (extensión nativa SQLite)

| Métrica | ChromaDB | **sqlite-vec** | pgvector |
|---|---|---|---|
| RAM en reposo | 200MB–1GB | **<10MB adicionales** | Requiere Postgres completo |
| Despliegue | Contenedor adicional | **Archivo .so nativo** | Docker imagen Postgres |
| Rendimiento <100k vectores | Sub-ms | **Sub-ms** | Excelente pero con overhead |
| Backups | Complejo | **`cp thdora.db`** | Requiere pg_dump |

**Argumentos clave:**
- Desarrollado por Alex Garcia, consolidado en ecosistema Python 2025/2026
- Corre en el mismo proceso que FastAPI → latencia de transferencia ≈ 0
- Un solo archivo `.db` para todo: relacional + vectorial
- Latencia recuperación semántica <5ms

**Implementación prevista Sprint 6:**
```sql
CREATE VIRTUAL TABLE vec_nlp_history USING vec_slots(
  id INTEGER PRIMARY KEY,
  embedding float[384]  -- all-MiniLM-L6-v2 local via Ollama
);
```

```python
# requirements.txt (añadir)
sqlite-vec>=0.1.0
```

**NO instalar ChromaDB en Madre.**

---

*Generado: 17 jun 2026 — Investigación Gemini — Aplica a Sprint 5-6*
