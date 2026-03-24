# thdora 🤖

> **Asistente personal con IA local**  
> Bot Telegram + FastAPI + Ollama (qwen2.5-coder:7b) + OpenClaw

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-local-black.svg)](https://ollama.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/Status-Active%20Development-orange.svg)]()

---

## 🦭 Navegación rápida

| Quiero... | Ir a |
|-----------|------|
| Entender qué es thdora | [Este README ↓](#qué-es-thdora) |
| Ver el plan del proyecto | [🗂️ ROADMAP.md](ROADMAP.md) |
| Ver cambios recientes | [📝 CHANGELOG.md](CHANGELOG.md) |
| Montar el entorno local | [⚙️ Setup entorno](docs/setup/entorno-local.md) |
| Entender la arquitectura | [🏗️ ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) |
| Ver decisiones técnicas | [📚 ADRs](docs/architecture/decisions/) |
| Ver toda la documentación | [📂 Índice docs](docs/INDEX.md) |
| Entender relación con thea-ia | [🔍 ADR-004](docs/architecture/decisions/ADR-004-relacion-thea-ia.md) |
| Ver historial de trabajo | [📅 Diarios](docs/diarios/) |

---

## ❓ Qué es thdora

thdora es un **asistente personal con IA local** diseñado para correr en tu propia máquina, sin APIs de pago, sin enviar datos a terceros.

- 📅 **Gestión de citas y hábitos** — JsonLifeManager con persistencia local
- 🤖 **IA privada local** — Ollama + qwen2.5-coder:7b sobre GTX 1060
- 📱 **Bot Telegram** — acceso desde el móvil, siempre disponible
- ⚡ **API REST** — FastAPI para integraciones
- 🔧 **OpenClaw** — control de repos GitHub desde el bot

**thdora es la evolución de [thea-ia](https://github.com/alvarofernandezmota-tech/thea-ia)** — misma visión, arquitectura más limpia. Ver [ADR-004](docs/architecture/decisions/ADR-004-relacion-thea-ia.md).

---

## 🖥️ Hardware y stack local

| Componente | Detalle |
|-----------|----------|
| CPU | Intel i5-8400 (6 núcleos) |
| RAM | 16 GB |
| GPU | NVIDIA GTX 1060 — 6 GB VRAM (CUDA 6.1) |
| SO | Windows 11 + WSL2 + Ubuntu 22.04 |
| LLM | qwen2.5-coder:7b via Ollama |
| Gateway | OpenClaw 127.0.0.1:18789 |
| Bot | Telegram (emparejado con OpenClaw) |

---

## 🏗️ Arquitectura

```
thdora/
├── src/
│   ├── core/
│   │   ├── interfaces/     ← contratos ABC (LifeManager, etc.)
│   │   └── impl/           ← implementaciones (Memory, Json, ...)
│   ├── api/             ← FastAPI endpoints
│   ├── bot/             ← Bot Telegram
│   └── ai/              ← Ollama + agentes
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   ├── INDEX.md         ← índice maestro de toda la doc
│   ├── architecture/    ← ARCHITECTURE.md + ADRs
│   ├── setup/           ← entorno local, CUDA, Ollama
│   ├── auditoria/       ← auditoría de thea-ia
│   ├── modules/         ← doc por módulo
│   └── diarios/         ← diario técnico diario
├── datos/             ← persistencia JSON local (.gitignore)
├── docker/
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
pip install -e ".[dev]"

# Verificar que todo funciona
pytest tests/
# ✅ 13 tests passing
```

Para el entorno completo (Ollama, OpenClaw, CUDA, Telegram) → ver [docs/setup/entorno-local.md](docs/setup/entorno-local.md).

---

## 📊 Estado del proyecto

| Módulo | Estado | Fase |
|--------|--------|------|
| `core/interfaces` | ✅ Completo | Fase 3 |
| `core/impl/MemoryLifeManager` | ✅ Completo + 13 tests | Fase 4 |
| `core/impl/JsonLifeManager` | 🔄 En progreso | Fase 5 |
| `api` FastAPI | ⏳ Esqueleto | Fase 6 |
| `bot` Telegram | ⏳ Pendiente | Fase 7 |
| `ai` Ollama | ⏳ Pendiente | Fase 9 |
| CUDA activado | ⚠️ Pendiente | Setup |

---

## 🧯 Ecosistema

```
alvarofernandezmota-tech/
├── thea-ia    ← proyecto original (intacto, historia, referencia de código)
├── thdora     ← este repo (proyecto activo)
└── personal   ← diario personal y vida
```

---

## ✍️ Autor

**Álvaro Fernández Mota** — [@alvarofernandezmota-tech](https://github.com/alvarofernandezmota-tech)
