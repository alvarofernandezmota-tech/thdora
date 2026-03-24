# Arquitectura de THDORA

## Visión general

THDORA es un **monorepo** que contiene todos los componentes del ecosistema
de gestión personal con IA local. Cada módulo es independiente pero comparte
las interfaces del núcleo (`src/core/interfaces/`).

## Capas del sistema

```
┌──────────────────────────────────────────────────────┐
│  CAPA DE ACCESO (Interfaces de usuario)         │
│  src/bot/     ← Telegram Bot                   │
│  src/api/     ← FastAPI REST                   │
│  src/core/bot/ ← CLI                           │
└───────────────────┬──────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────────┐
│  CAPA DE IA (src/ai/)                           │
│  Ollama client → mistral-nemo:12b              │
│  Training scripts → fine-tuning con datos      │
└───────────────────┬──────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────────┐
│  CAPA CORE (src/core/)                          │
│  interfaces/ ← Contratos ABC                   │
│  impl/       ← Implementaciones concretas       │
└──────────────────────────────────────────────────────┘
```

## Principios de diseño

| Principio | Aplicación |
|-----------|------------|
| **Dependency Inversion** | Las capas superiores dependen de `AbstractLifeManager`, no de implementaciones concretas |
| **Open/Closed** | Añadir `JsonLifeManager` no requiere modificar nada existente |
| **Single Responsibility** | Cada módulo tiene una única responsabilidad |
| **Interface Segregation** | Las interfaces son pequeñas y cohesivas |

## Decisiones técnicas

Ver [decisions/](decisions/) para los ADRs (Architecture Decision Records).
