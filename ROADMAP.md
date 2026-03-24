# 🗺️ THDORA — ROADMAP

## Estado: v0.4.0 — 24 marzo 2026

```
[████████████████████████] 100% ✅ FASE 1: Interfaces abstractas (AbstractLifeManager)
[████████████████████████] 100% ✅ FASE 2: MemoryLifeManager (CRUD en memoria)
[████████████████████████] 100% ✅ FASE 3: Bot CLI interactivo
[████████████░░░░░░░░░░░░]  50% 🔄 FASE 4: Monorepo enterprise + docs exhaustivos
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 5: Persistencia JSON + tests unitarios
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 6: FastAPI REST
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 7: Bot Telegram
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 8: Ollama IA local (mistral-nemo:12b)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 9: Fine-tuning con datos propios
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 10: CI/CD + Docker + Deploy
```

---

## ✅ FASE 1-3 — Completadas

- `AbstractLifeManager` — interfaz ABC con citas + hábitos
- `MemoryLifeManager` — implementación en memoria con UUID
- Bot CLI interactivo con menú

---

## 🔄 FASE 4 — Monorepo enterprise (EN CURSO)

- [x] Migración AppointmentManager → `src/core/`
- [x] Estructura enterprise completa
- [x] Documentación de interfaces y módulos
- [ ] Completar docs de cada método
- [ ] `pyproject.toml` completo
- [ ] `Makefile` con comandos de desarrollo

---

## ⏳ FASE 5 — Persistencia + Tests

- [ ] `JsonLifeManager` — implementación con JSON
- [ ] `src/core/impl/json_lifemanager.py`
- [ ] Tests unitarios con pytest
- [ ] Coverage >80%
- [ ] Pre-commit hooks

---

## ⏳ FASE 6 — FastAPI REST

- [ ] `GET /appointments/{date}` — citas del día
- [ ] `POST /appointments` — crear cita
- [ ] `DELETE /appointments/{id}` — eliminar
- [ ] `GET /habits/{date}` — hábitos del día
- [ ] `POST /habits` — registrar hábito
- [ ] `GET /summary/{date}` — resumen del día
- [ ] Swagger UI automático
- [ ] Pydantic models

---

## ⏳ FASE 7 — Bot Telegram

- [ ] Setup `python-telegram-bot`
- [ ] `/citas` — ver citas del día
- [ ] `/nueva` — crear cita (ConversationHandler)
- [ ] `/habito` — registrar hábito
- [ ] `/resumen` — resumen del día
- [ ] Notificaciones automáticas 15 min antes

---

## ⏳ FASE 8 — Ollama IA local

**Hardware objetivo:** GTX 1060 6GB VRAM + 16GB RAM  
**Modelo:** `mistral-nemo:12b` (offload híbrido GPU+CPU)

```bash
# Config Ollama
export OLLAMA_NUM_GPU=35
export OLLAMA_GPU_OVERHEAD=200
export OLLAMA_MAX_LOADED_MODELS=1
```

- [ ] Activar CUDA en WSL2
- [ ] Instalar Ollama + `mistral-nemo:12b`
- [ ] `src/ai/ollama_client.py` — cliente Ollama
- [ ] Conectar con bot Telegram
- [ ] Comandos de consulta libre: `/pregunta <texto>`

---

## ⏳ FASE 9 — Fine-tuning con datos propios

- [ ] Recopilar datasets de conversaciones propias
- [ ] `src/ai/training/` — scripts de fine-tuning
- [ ] LoRA/QLoRA para modelo personalizado
- [ ] Evaluación y benchmarks
- [ ] Modelo exportado y versionado

---

## ⏳ FASE 10 — CI/CD + Docker

- [ ] GitHub Actions — tests automáticos en cada push
- [ ] GitHub Actions — linting (black + flake8)
- [ ] `Dockerfile` + `docker-compose.yml`
- [ ] Deploy en Railway/VPS

---

_Actualizado: 24 marzo 2026_
