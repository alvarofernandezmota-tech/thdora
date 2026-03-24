# THDORA 🤖

> **Ecosistema de gestión personal con IA local**  
> Bot Telegram + FastAPI + Ollama (mistral-nemo:12b) + AppointmentManager

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active Development](https://img.shields.io/badge/Status-Active%20Development-orange.svg)]()
[![Part of THEA IA](https://img.shields.io/badge/Part%20of-THEA%20IA-purple.svg)]()

---

## 🌟 ¿Qué es THDORA?

THDORA es un **asistente personal con IA local** que combina:

- 📅 **Gestión de citas y hábitos** — AppointmentManager integrado
- 🤖 **IA privada local** — Ollama + mistral-nemo:12b, sin costes, sin enviar datos a terceros
- 📱 **Bot Telegram** — acceso desde cualquier dispositivo
- ⚡ **API REST** — FastAPI para integración con otros sistemas
- 📓 **Diario personal** — tracking de sesiones y decisiones

---

## 🏗️ Arquitectura

```
thdora/
├── src/
│   ├── core/           ← Lógica de negocio central
│   │   ├── interfaces/  ← Contratos abstractos (ABC)
│   │   └── impl/        ← Implementaciones concretas
│   ├── api/            ← FastAPI endpoints
│   ├── bot/            ← Bot Telegram
│   └── ai/             ← Ollama + fine-tuning
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   ├── architecture/   ← Diagramas y decisiones (ADR)
│   ├── api/            ← Documentación de cada endpoint
│   ├── modules/        ← Documentación de cada módulo
│   └── diarios/        ← Diario de desarrollo
├── .github/
│   └── workflows/      ← CI/CD GitHub Actions
├── docker/             ← Docker + Compose
├── datos/              ← Persistencia JSON local
├── pyproject.toml
├── Makefile
├── ROADMAP.md
└── CHANGELOG.md
```

---

## 🚀 Instalación rápida

```bash
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Ejecutar bot CLI
python src/core/bot/thdora_bot.py

# Ejecutar API
uvicorn src.api.main:app --reload
```

---

## 📊 Estado del proyecto

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| `core/interfaces` | ✅ v1.0 | Contratos ABC |
| `core/impl` | ✅ v1.0 | MemoryLifeManager |
| `core/bot` | ✅ v1.0 | CLI interactivo |
| `api` | ⏳ v0.1 | FastAPI esqueleto |
| `bot` | ⏳ pendiente | Telegram |
| `ai` | ⏳ pendiente | Ollama local |

---

## 📖 Documentación

- [Arquitectura del sistema](docs/architecture/ARCHITECTURE.md)
- [Decisiones técnicas (ADR)](docs/architecture/decisions/)
- [Módulo core](docs/modules/core.md)
- [Módulo API](docs/modules/api.md)
- [Diario de desarrollo](docs/diarios/)
- [ROADMAP](ROADMAP.md)
- [CHANGELOG](CHANGELOG.md)

---

## ✍️ Autor

**Álvaro Fernández Mota** — [@alvarofernandezmota-tech](https://github.com/alvarofernandezmota-tech)  
Metodología EscuelaMusk — *"Aprende construyendo sistemas reales."*
