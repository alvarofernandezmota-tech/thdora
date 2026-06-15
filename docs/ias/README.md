# IAs en THDORA
*Última actualización: 15 junio 2026*

## Stack actual

| IA | Rol en THDORA | Estado |
|----|--------------|--------|
| **Groq (llama-3.3-70b-versatile)** | Motor NLP de Toki en producción | 🟢 Activo |
| **Grok (xAI)** | Investigación + generación de código | 🟢 Activo |
| **Claude (Perplexity)** | Documentación + push al repo | 🟢 Activo |
| **Mistral** | Investigación + código (en proceso) | 🟡 Parcial |
| **Gemini** | Estudios de mercado, contexto largo | 🟢 Activo |

## Decisiones de arquitectura NLP

- **Motor actual:** Groq free tier con `llama-3.3-70b-versatile` (128k contexto)
- **Framework agentes:** LangChain → evolución a LangGraph para Toki stateful
- **Function calling:** implementado en v0.17.0 (Bloque 1.4)
- **Memoria:** corta en `user_data` (sesión) → persistente en SQLite (Bloque 2.1 pendiente)

## Trazabilidad de decisiones

| Fecha | Decisión | IA que la generó | Output |
|-------|---------|-----------------|--------|
| 14 jun 2026 | Modelo Groq: llama3-8b → llama-3.3-70b-versatile | Diagnóstico manual | `fix: update Groq model` |
| 15 jun 2026 | Bloque 1 completo: anti-timeout + system prompt Toki + function calling | Grok (xAI) | `src/bot/handlers/nlp.py` + `src/bot/groq_router.py` |
| 15 jun 2026 | Arquitectura futura: LangGraph + repository pattern + tool registry | Grok (xAI) | `docs/ias/auditoria-tecnica.md` |
