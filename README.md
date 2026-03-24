# THDORA Bot 📅

> **Sistema de gestión de citas con arquitectura modular profesional**

Módulo Python del ecosistema THEA IA que implementa gestión completa de tiempo y productividad mediante arquitectura de 3 capas, separación de responsabilidades y principios SOLID.

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active Development](https://img.shields.io/badge/Status-Active%20Development-green.svg)](https://github.com/alvarofernandezmota-tech/thdora)
[![Part of THEA IA](https://img.shields.io/badge/Part%20of-THEA%20IA-purple.svg)](https://github.com/alvarofernandezmota-tech)

---

## 🌟 Contexto del Proyecto

THDORA Bot es un componente del **proyecto THEA IA** — sistema completo de automatización e inteligencia artificial para gestión personal. Este módulo implementa la capa de gestión de tiempo y citas, diseñado como:

- **Microservicio independiente:** Arquitectura desacoplada para integración futura
- **Prototipo funcional:** Validación de conceptos antes de integración con THEA IA
- **Base escalable:** Preparado para migración a API REST + Bot Telegram + Ollama local

### Stack objetivo

```
THDORA
  ├── FastAPI          ← API REST
  ├── Bot Telegram     ← Interfaz móvil
  ├── Ollama local     ← IA local (mistral-nemo:12b)
  │     └── GTX 1060 6GB VRAM + 6GB RAM
  └── AppointmentManager ← Core de citas
```

---

## 🏗️ Arquitectura actual (v1.0)

### Diseño de 3 capas

```
┌─────────────────────────────────────────┐
│  PRESENTATION LAYER (UI)                │
│  thdora_bot.py                          │
│  - Interfaz CLI interactiva             │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  BUSINESS LOGIC LAYER                   │
│  thdora_functions.py                    │
│  - Operaciones CRUD                     │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  DATA LAYER                             │
│  thdora_data.py                         │
│  - Estructura de datos centralizada     │
└─────────────────────────────────────────┘
```

---

## ⚡ Estado actual

| Fase | Descripción | Estado |
|------|-------------|--------|
| Fase 1 | CRUD completo | ✅ 100% |
| Fase 2 | Bot CLI interactivo | ✅ 100% |
| Fase 3 | Arquitectura modular | ✅ 100% |
| Fase 4 | Persistencia JSON | 🔄 25% |
| Fase 5 | Tests unitarios | ⏳ |
| Fase 6 | Logging y errores | ⏳ |
| Fase 7 | FastAPI REST | ⏳ |
| Fase 8 | Bot Telegram | ⏳ |
| Fase 9 | Ollama IA local | ⏳ |

---

## 🚀 Instalación

```bash
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora
python src/thdora_bot.py
```

---

## 📁 Estructura

```
thdora/
├── src/
│   ├── thdora_data.py         # Capa de datos
│   ├── thdora_functions.py    # Lógica de negocio
│   └── thdora_bot.py          # Presentación CLI
├── docs/                      # Documentación técnica
├── datos/                     # JSON persistencia
├── ROADMAP.md                 # Plan completo
└── README.md                  # Este archivo
```

---

## 🔗 Roadmap completo

Ver [ROADMAP.md](./ROADMAP.md) para el plan completo de desarrollo.

---

## ✍️ Autor

**Álvaro Fernández Mota**  
[@alvarofernandezmota-tech](https://github.com/alvarofernandezmota-tech)  
Metodología: EscuelaMusk — *"Aprende construyendo sistemas reales."*

---
_Migrado desde repo personal → repo independiente: 24 marzo 2026_
