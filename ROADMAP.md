# 🗺️ THDORA — ROADMAP COMPLETO

**De CLI a asistente IA personal completo**

---

## 📊 Estado actual

**Versión:** v0.3.0  
**Fecha última actualización:** 24 marzo 2026  
**Origen:** Migrado desde `personal/03_proyectos/thdora`

```
[████████████████████████] 100% ✅ FASE 1: CRUD Completo
[████████████████████████] 100% ✅ FASE 2: Bot CLI Interactivo
[████████████████████████] 100% ✅ FASE 3: Arquitectura Modular
[████████░░░░░░░░░░░░░░░░]  25% 🔄 FASE 4: Persistencia JSON
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 5: Tests Unitarios
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 6: Logging y Errores
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 7: FastAPI REST
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 8: Bot Telegram
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 9: Ollama IA local
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 10: CI/CD y Deploy
```

---

## ✅ FASE 1-3 — COMPLETADAS

- Fase 1: CRUD completo en memoria
- Fase 2: Bot CLI interactivo con menú
- Fase 3: Refactorización a arquitectura modular 3 capas

**Hitos:**
- Primera función `agregar_cita()` — 6 feb 2026
- CRUD completo — 8 feb 2026
- Arquitectura modular — 8 feb 2026 ⭐

---

## 🔄 FASE 4 — Persistencia JSON (25%)

- [x] 13A: Template `guardar_json()` creado
- [ ] 13B: Módulo `thdora_json.py`
- [ ] 14A: `cargar_json()`
- [ ] 15A: Bot con persistencia completa
- [ ] 16A: Estructura profesional (`__init__.py`, `requirements.txt`)

---

## ⏳ FASE 5 — Tests Unitarios

- [ ] Setup pytest
- [ ] Tests CRUD
- [ ] Tests JSON
- [ ] Coverage >80%
- [ ] Pre-commit hooks

---

## ⏳ FASE 6 — Logging y Errores

- [ ] Logging profesional con niveles
- [ ] Excepciones personalizadas
- [ ] Validación robusta de inputs

---

## ⏳ FASE 7 — FastAPI REST

- [ ] Endpoints CRUD `/citas`
- [ ] Pydantic models
- [ ] Swagger docs automáticos
- [ ] Tests API

---

## ⏳ FASE 8 — Bot Telegram

- [ ] Setup `python-telegram-bot`
- [ ] Comandos CRUD via Telegram
- [ ] ConversationHandler para flujos
- [ ] Notificaciones automáticas
- [ ] Integración con FastAPI

---

## ⏳ FASE 9 — Ollama IA local

**Hardware:** GTX 1060 6GB VRAM + 16GB RAM  
**Modelo objetivo:** `mistral-nemo:12b` (sweet spot inteligencia/VRAM)

- [ ] Activar CUDA en WSL2
- [ ] Configurar `mistral-nemo:12b` con offload híbrido
- [ ] Integrar Ollama con FastAPI
- [ ] Conectar bot Telegram con IA local
- [ ] Configurar OpenClaw gateway
- [ ] Destinar 6GB VRAM + 6GB RAM al modelo

**Config Ollama objetivo:**
```bash
export OLLAMA_NUM_GPU=35
export OLLAMA_GPU_OVERHEAD=200
export OLLAMA_MAX_LOADED_MODELS=1
```

---

## ⏳ FASE 10 — CI/CD y Deploy

- [ ] GitHub Actions — tests automáticos
- [ ] GitHub Actions — linting
- [ ] Docker + Docker Compose
- [ ] Deploy cloud (Railway/Heroku)

---

## 🎯 Visión final

```
THDORA (asistente IA personal)
  ├── Bot Telegram        ← acceso desde móvil 24/7
  ├── FastAPI             ← API REST
  ├── Ollama local        ← IA privada, sin coste
  │     └── mistral-nemo:12b
  ├── AppointmentManager  ← gestión de citas
  └── Integración GitHub  ← lectura/edición repos
```

---

_Actualizado: 24 marzo 2026 | Migrado a repo independiente_
