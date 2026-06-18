#!/usr/bin/env python3
"""
scripts/ai_audit.py — Auditoría unificada Claude / Grok / xAI

Lee el código real del repo, lo envía a la IA configurada
y genera un reporte de bugs de runtime, mismatches API
y tests pytest urgentes.

Uso:
    ANTHROPIC_API_KEY=xxx python scripts/ai_audit.py
    GROK_API_KEY=xxx     python scripts/ai_audit.py
    XAI_API_KEY=xxx      python scripts/ai_audit.py

El reporte se guarda en: audit_report.md
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.error

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_URL = "https://raw.githubusercontent.com/alvarofernandezmota-tech/thdora/main"

FILES_TO_AUDIT = [
    "src/bot/main.py",
    "src/bot/handlers/nlp.py",
    "src/bot/handlers/nlp_disambig.py",
    "src/bot/handlers/stats.py",
    "src/bot/handlers/voice.py",
    "src/bot/handlers/diario.py",
    "src/bot/handlers/weather.py",
    "src/agents/core/node.py",
    "src/agents/core/graph.py",
    "src/agents/tools/registry.py",
    "src/agents/tools/appointments.py",
    "src/agents/tools/habits.py",
    "src/agents/memory/manager.py",
    "src/api/main.py",
    "src/bot/api_client.py",
    "src/config.py",
    "src/agents/config.py",
    "src/db/base.py",
    "scripts/smoke_test.py",
]


def fetch_file(path: str) -> str:
    try:
        url = f"{BASE_URL}/{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "thdora-audit/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            content = r.read().decode("utf-8")
            snippet = content[:2800]
            if len(content) > 2800:
                snippet += f"\n... [truncado {len(content)} chars]"
            return f"### {path}\n```python\n{snippet}\n```"
    except urllib.error.HTTPError as e:
        return f"### {path}\n[HTTP {e.code} — archivo no encontrado]"
    except Exception as e:
        return f"### {path}\n[ERROR: {e}]"


def build_prompt(code_blocks: list) -> str:
    code = "\n\n".join(code_blocks)
    return f"""Eres un QA Engineer senior especializado en Python, FastAPI, LangGraph, python-telegram-bot v21 y Docker.

Proyecto: THDORA (Bot Telegram personal con FastAPI + SQLite + LangGraph + Groq).

Tareas obligatorias:

1. BUGS DE RUNTIME — Detecta problemas que solo aparecen al ejecutar (no al importar):
   - KeyError, AttributeError, TypeError con datos reales
   - Mismatches entre ThdoraApiClient y endpoints de la API (rutas, params, tipos)
   - Edge cases sin manejar: None, lista vacía, timeout, user_id 0
   - Race conditions o estado compartido problemático

2. FLUJO SIMULADO — Simula este flujo completo:
   Usuario: "mañana tengo dentista a las 10"
   → nlp_handler detecta intención
   → llama a api_client.create_appointment(...)
   → API guarda en SQLite
   → responde al usuario
   Para cada paso: ✅ OK / ⚠️ RIESGO / ❌ FALLO con causa exacta.

3. 5 TESTS PYTEST — Genera tests críticos completos con pytest + mocks.
   Usa AsyncMock para async, patch para dependencias externas.
   Código completo y ejecutable.

FORMATO DE RESPUESTA:
- PROBLEMA #N — [CRÍTICO / MEDIO / BAJO]
- Archivo: src/xxx.py  línea: XX
- Causa: descripción exacta
- Fix: código listo para copiar
- Tabla final: # | Severidad | Archivo | Causa | Fix en 1 línea

Solo problemas REALES vistos en el código. Si algo está bien, di OK.

CÓDIGO A ANALIZAR:
{code}
""".strip()


def ask_claude(prompt: str) -> str:
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        response = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in response.content if hasattr(b, "text"))
    except ImportError:
        raise RuntimeError("Instala anthropic: pip install anthropic")
    except Exception as e:
        raise RuntimeError(f"Error Claude: {e}")


def ask_grok(prompt: str) -> str:
    api_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY", "")
    payload = json.dumps({
        "model": os.getenv("GROK_MODEL", "grok-2-1212"),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4096,
    }).encode()
    req = urllib.request.Request(
        os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions"),
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Error Grok {e.code}: {e.read().decode()[:300]}")


def main():
    print(f"\n🧠 THDORA AI Audit — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 55)

    print("\n📥 Leyendo archivos del repo...")
    code_blocks = []
    for path in FILES_TO_AUDIT:
        block = fetch_file(path)
        status = "✅" if "ERROR" not in block and "HTTP" not in block else "⚠️ "
        print(f"  {status} {path}")
        code_blocks.append(block)

    prompt = build_prompt(code_blocks)
    print(f"\n📝 Prompt: {len(prompt)} chars — {len(code_blocks)} archivos")

    # Elegir IA disponible
    if os.getenv("ANTHROPIC_API_KEY"):
        ia_name = "Claude"
        print("\n🤖 Usando Claude (Anthropic)...")
        result = ask_claude(prompt)
    elif os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY"):
        ia_name = "Grok/xAI"
        print("\n🤖 Usando Grok (xAI)...")
        result = ask_grok(prompt)
    else:
        print("\n❌ Define ANTHROPIC_API_KEY o GROK_API_KEY en .env")
        print("   Ejemplo: ANTHROPIC_API_KEY=sk-ant-xxx python scripts/ai_audit.py")
        sys.exit(1)

    print("\n" + "=" * 55)
    print(result)
    print("=" * 55)

    report = f"""# THDORA AI Audit Report
_Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} por {ia_name}_

---

{result}

---
_Archivos analizados: {len(code_blocks)} — Modelo: {ia_name}_
"""
    Path("audit_report.md").write_text(report, encoding="utf-8")
    print(f"\n✅ Reporte guardado en audit_report.md")
    print("   Siguiente paso: pegar el contenido en Perplexity para aplicar fixes al repo.\n")


if __name__ == "__main__":
    main()
