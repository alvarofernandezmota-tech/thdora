# Auditoría Técnica THDORA v0.16.4
*Generado por Grok (xAI) | 15 junio 2026*

## Diagnóstico actual

**Puntuación actual: 6.2/10** — funcional pero frágil para crecimiento.

### Problemas identificados

- Monolito desorganizado: Todo en `src/bot/` mezclado (handlers, router, api_client)
- Duplicación: Lógica de citas/habitos repetida entre handlers y NLP
- Estado disperso: Memoria corta en `user_data` + SQLite sin unificar
- Falta de patrones modernos: No hay CQRS, no hay dependency injection, logging básico, testing débil
- Escalabilidad: Difícil añadir WhatsApp, multi-tenant, o más agentes
- Timeout NLP: modelo 70b tarda más, timeout cliente demasiado corto → fix en Bloque 1.1

## Target: 9/10

### Nueva estructura recomendada

```
src/
├── core/                  # Núcleo reutilizable
│   ├── config.py
│   ├── logger.py
│   ├── dependencies.py
│   ├── models.py
│   └── exceptions.py
├── agents/
│   └── toki/
│       ├── prompt.py       # SystemPromptBuilder
│       ├── tools.py        # Tool registry con decorador @toki_tool
│       ├── memory.py       # Memoria persistente por usuario
│       └── router.py       # TokiRouter limpio
├── handlers/              # Telegram handlers slim
├── api/                   # FastAPI routes
├── services/              # Business logic
├── repository/            # Data access layer
├── schemas/               # Pydantic models
└── utils/
```

## Plan de acción (7 días)

| Día | Tarea | Responsable |
|-----|-------|-------------|
| 1-2 | Nueva estructura + repository pattern | Grok/Mistral + Claude |
| 3 | Tool registry + prompt builder | Grok |
| 4 | Memoria persistente + mood detection | Grok/Mistral |
| 5-6 | Refactor handlers slim + DI | Grok |
| 7 | Tests + ROADMAP actualizado + commit grande | Claude |

## Métricas de éxito post-refactor

| Métrica | Actual | Target |
|---------|--------|--------|
| LOC handlers | ~120k | -30% |
| Tiempo respuesta NLP | ~3s | <1.8s |
| Cobertura tests | ~40% | 80% |
| Tiempo nueva feature | ~3 días | <2 días |

## Próximos bloques de código pendientes

- [ ] Bloque 2.1: Memoria persistente (tabla `conversations` en SQLite)
- [ ] Bloque 2.2: Mood detection silencioso
- [ ] Bloque 3: Multiusuario (`user_id` en todos los endpoints)
- [ ] Bloque 4: Métricas (tabla `events` + comando `/stats`)
- [ ] Refactor mayor: nueva estructura `agents/toki/`
