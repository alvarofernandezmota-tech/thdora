#!/usr/bin/env python3
"""
scripts/ai_audit.py
Auditóría automática de THDORA usando Mistral AI.

Lee el código real del repo, lo envía a Mistral y genera un reporte
de bugs de runtime, mismatches API y tests pytest urgentes.

Uso:
    MISTRAL_API_KEY=xxx python scripts/ai_audit.py
    # o con .env cargado:
    python scripts/ai_audit.py

El reporte se guarda en: audit_report.md
"""
import os
import sys
import urllib.request
import urllib.error
import json
from datetime import datetime
from pathlib import Path

# Intentar cargar .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv no instalado, continuar con variables de entorno

API_KEY = os.getenv("MISTRAL_API_KEY", "")
if not API_KEY:
    print("\n\u274c Falta MISTRAL_API_KEY")
    print("   Uso: MISTRAL_API_KEY=tu_clave python scripts/ai_audit.py")
    print("   O a\u00f1ade MISTRAL_API_KEY=tu_clave al archivo .env")
    sys.exit(1)

BASE = "https://raw.githubusercontent.com/alvarofernandezmota-tech/thdora/main"

FILES_TO_AUDIT = [
    # Bot principal
    "src/bot/main.py",
    # Handlers
    "src/bot/handlers/nlp.py",
    "src/bot/handlers/nlp_disambig.py",
    "src/bot/handlers/stats.py",
    "src/bot/handlers/voice.py",
    "src/bot/handlers/diario.py",
    "src/bot/handlers/weather.py",
    # Agente
    "src/agents/core/node.py",
    "src/agents/core/graph.py",
    "src/agents/tools/registry.py",
    "src/agents/tools/appointments.py",
    "src/agents/tools/habits.py",
    "src/agents/memory/manager.py",
    # API
    "src/api/main.py",
    "src/bot/api_client.py",
    # Config
    "src/config.py",
    "src/agents/config.py",
    # DB
    "src/db/base.py",
    # Smoke test
    "scripts/smoke_test.py",
]

PASS = "\u2705"
FAIL = "\u274c"
WARN = "\u26a0\ufe0f "


def fetch(path: str) -> str:
    url = f"{BASE}/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "thdora-audit/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            content = r.read().decode()
            return content
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"[ARCHIVO NO ENCONTRADO: {path}]"
        return f"[HTTP ERROR {e.code} leyendo {path}]"
    except Exception as e:
        return f"[ERROR leyendo {path}: {e}]"


def ask_mistral(prompt: str, model: str = "mistral-large-latest") -> str:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4096,
    }).encode()

    req = urllib.request.Request(
        "https://api.mistral.ai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        raise RuntimeError(f"Mistral API error {e.code}: {body}")


def build_prompt(code_sections: list[str]) -> str:
    all_code = "\n\n".join(code_sections)
    return f"""Eres un experto QA engineer especializado en Python, FastAPI, LangGraph y bots Telegram.
Proyecto: THDORA \u2014 bot Telegram personal con FastAPI + SQLite + LangGraph + Groq.

Analiza el c\u00f3digo que te paso y ejecuta estas 3 fases:

\u2550\u2550\u2550\u2550 FASE 1 \u2014 BUGS DE RUNTIME (no de import) \u2550\u2550\u2550\u2550
Detecta bugs que solo aparecen al ejecutar, no al importar:
- KeyError, AttributeError, TypeError en datos reales
- Mismatches entre lo que ThdoraApiClient llama y lo que la API expone
  (rutas, par\u00e1metros, tipos de respuesta)
- Casos edge sin manejar: None, lista vac\u00eda, timeout, user_id 0
- Condiciones de carrera o estado compartido problem\u00e1tico

\u2550\u2550\u2550\u2550 FASE 2 \u2014 FLUJO SIMULADO \u2550\u2550\u2550\u2550
Simula mentalmente este flujo completo:
  Usuario escribe \"ma\u00f1ana tengo dentista a las 10\"
  \u2192 nlp_handler detecta intenci\u00f3n \"crear_cita\"
  \u2192 llama a api_client.create_appointment(...)
  \u2192 API guarda en SQLite
  \u2192 responde al usuario

Para cada paso: \u2705 OK / \u26a0\ufe0f RIESGO / \u274c FALLO con causa exacta.

\u2550\u2550\u2550\u2550 FASE 3 \u2014 TESTS PYTEST URGENTES \u2550\u2550\u2550\u2550
Genera los 5 tests m\u00e1s cr\u00edticos, completos y ejecutables con pytest.
Usa unittest.mock para evitar llamadas reales a Groq/Telegram/SQLite.
Formato exacto:
```python
# tests/unit/test_nombre.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
# ... c\u00f3digo completo ejecutable
```

\u2550\u2550\u2550\u2550 FORMATO DE RESPUESTA \u2550\u2550\u2550\u2550

FASE 1 \u2014 Para cada problema real:
PROBLEMA #N \u2014 [CR\u00cdTICO / MEDIO / BAJO]
Archivo: src/xxx.py  l\u00ednea: XX
Causa: descripci\u00f3n exacta
Fix: c\u00f3digo listo para aplicar

FASE 2 \u2014 Paso a paso con \u2705/\u26a0\ufe0f/\u274c

FASE 3 \u2014 C\u00f3digo pytest completo

Tabla final priorizada: # | Severidad | Archivo | Causa | Fix en 1 l\u00ednea

Solo problemas REALES vistos en el c\u00f3digo. Si algo est\u00e1 bien, di OK y pasa al siguiente.

\u2550\u2550\u2550\u2550 C\u00d3DIGO A ANALIZAR \u2550\u2550\u2550\u2550

{all_code}
"""


if __name__ == "__main__":
    print("\n\U0001f9e0 THDORA AI Audit \u2014 Mistral Large")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Archivos a auditar: {len(FILES_TO_AUDIT)}\n")

    # 1. Leer archivos del repo
    print("\U0001f4e6 Leyendo archivos del repo...")
    code_sections = []
    errors = []
    for path in FILES_TO_AUDIT:
        content = fetch(path)
        if content.startswith("[ERROR") or content.startswith("[ARCHIVO") or content.startswith("[HTTP"):
            print(f"  {WARN} {path} \u2192 {content[:60]}")
            errors.append(path)
        else:
            # Limitar a 2500 chars por archivo para no superar el contexto
            snippet = content[:2500]
            if len(content) > 2500:
                snippet += f"\n... [truncado a 2500/{len(content)} chars]"
            code_sections.append(f"### {path}\n```python\n{snippet}\n```")
            print(f"  {PASS} {path} ({len(content)} chars)")

    if errors:
        print(f"\n{WARN} {len(errors)} archivos no encontrados \u2014 continuar de todas formas")

    if not code_sections:
        print(f"\n{FAIL} No se pudo leer ning\u00fan archivo. Revisa la conexi\u00f3n.")
        sys.exit(1)

    # 2. Construir prompt
    prompt = build_prompt(code_sections)
    print(f"\n\U0001f4dd Prompt generado: {len(prompt)} chars")

    # 3. Llamar a Mistral
    print("\n\U0001f916 Consultando Mistral AI (puede tardar 20-40s)...\n")
    try:
        result = ask_mistral(prompt)
    except RuntimeError as e:
        print(f"{FAIL} Error de API: {e}")
        sys.exit(1)

    # 4. Mostrar resultado
    print("\n" + "=" * 50)
    print(result)
    print("=" * 50)

    # 5. Guardar reporte
    report_path = Path("audit_report.md")
    report_content = f"""# THDORA AI Audit Report
_Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} por Mistral Large_

---

{result}

---
_Archivos analizados: {len(code_sections)}/{len(FILES_TO_AUDIT)}_
"""
    report_path.write_text(report_content, encoding="utf-8")
    print(f"\n{PASS} Reporte guardado en {report_path.resolve()}")
    print("\nPr\u00f3ximo paso: revisa audit_report.md y p\u00e1sale los fixes a Perplexity para aplicarlos al repo.\n")
