#!/usr/bin/env python3
"""
Smoke test de pre-arranque para THDORA.

Ejecuta esta secuencia ANTES de `docker compose up` para detectar
todos los fallos posibles sin necesidad de levantar Docker.

Uso (desde la carpeta raiz del repo):
    python scripts/smoke_test.py

Requiere:
    pip install -r requirements.txt (o estar dentro del contenedor)
    .env con TELEGRAM_BOT_TOKEN y GROQ_API_KEY rellenos
"""
import sys
import os

# Asegura que src/ es importable desde la raiz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "
results = []


def check(name, fn):
    try:
        fn()
        print(f"{PASS} {name}")
        results.append((name, True, None))
    except Exception as exc:
        print(f"{FAIL} {name}\n     → {type(exc).__name__}: {exc}")
        results.append((name, False, exc))


# ------------------------------------------------------------------ #
# 1. ENTORNO
# ------------------------------------------------------------------ #

def test_env_file():
    assert os.path.exists(".env"), ".env no encontrado en la carpeta actual"

def test_data_dir():
    os.makedirs("data", exist_ok=True)
    assert os.path.isdir("data")

def test_dotenv_vars():
    from dotenv import dotenv_values
    env = dotenv_values(".env")
    missing = []
    for key in ["TELEGRAM_BOT_TOKEN", "GROQ_API_KEY"]:
        if not env.get(key):
            missing.append(key)
    assert not missing, f"Variables obligatorias sin valor: {missing}"

# ------------------------------------------------------------------ #
# 2. IMPORTS CLAVE
# ------------------------------------------------------------------ #

def test_import_langgraph():
    import langgraph

def test_import_langgraph_checkpoint_sqlite():
    from langgraph.checkpoint.sqlite import SqliteSaver

def test_import_langchain_groq():
    from langchain_groq import ChatGroq

def test_import_telegram():
    from telegram.ext import ApplicationBuilder

def test_import_fastapi():
    import fastapi

def test_import_apscheduler():
    import apscheduler

# ------------------------------------------------------------------ #
# 3. CONFIGURACION PYDANTIC
# ------------------------------------------------------------------ #

def test_settings_load():
    from src.config import settings
    assert settings.TELEGRAM_BOT_TOKEN, "TELEGRAM_BOT_TOKEN vacio"
    assert settings.GROQ_API_KEY, "GROQ_API_KEY vacio"

def test_agent_config_load():
    from src.agents.config import agent_config
    assert agent_config.memory_db_path

# ------------------------------------------------------------------ #
# 4. BASE DE DATOS
# ------------------------------------------------------------------ #

def test_db_init():
    from src.db.session import get_db
    with get_db() as db:
        assert db is not None

def test_sqlite_saver_init():
    from langgraph.checkpoint.sqlite import SqliteSaver
    os.makedirs("data", exist_ok=True)
    saver = SqliteSaver.from_conn_string("data/smoke_test.db")
    assert saver is not None
    # limpieza
    try:
        os.remove("data/smoke_test.db")
    except Exception:
        pass

# ------------------------------------------------------------------ #
# 5. GRAFO LANGGRAPH
# ------------------------------------------------------------------ #

def test_memory_manager_init():
    from src.agents.memory.manager import memory_manager
    assert memory_manager.checkpointer is not None

def test_build_thdora_graph():
    from src.agents import build_thdora_graph
    graph = build_thdora_graph()
    assert graph is not None

# ------------------------------------------------------------------ #
# 6. GROQ API (llamada real)
# ------------------------------------------------------------------ #

def test_groq_api_call():
    """Llama a Groq con un mensaje minimo para verificar token y conectividad."""
    from src.config import settings
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        max_tokens=10,
    )
    result = llm.invoke("responde solo: ok")
    assert result.content, "Groq devolvio respuesta vacia"

# ------------------------------------------------------------------ #
# 7. HANDLERS (solo import, sin ejecutar)
# ------------------------------------------------------------------ #

def test_import_handler_nlp():
    from src.bot.handlers.nlp import nlp_handler

def test_import_handler_stats():
    from src.bot.handlers.stats import stats_handler

def test_import_handler_diario():
    from src.bot.handlers.diario import diario_handler

def test_import_handler_weather():
    from src.bot.handlers.weather import weather_handler

def test_import_handler_voice():
    from src.bot.handlers.voice import voice_handler

# ------------------------------------------------------------------ #
# EJECUTAR
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    print("\n🧠 THDORA Smoke Test\n" + "=" * 40)

    print("\n[📦 Entorno]")
    check("Archivo .env existe", test_env_file)
    check("Carpeta data/ existe o se crea", test_data_dir)
    check("Variables obligatorias en .env", test_dotenv_vars)

    print("\n[🐍 Imports clave]")
    check("import langgraph", test_import_langgraph)
    check("import langgraph.checkpoint.sqlite", test_import_langgraph_checkpoint_sqlite)
    check("import langchain_groq", test_import_langchain_groq)
    check("import telegram", test_import_telegram)
    check("import fastapi", test_import_fastapi)
    check("import apscheduler", test_import_apscheduler)

    print("\n[⚙️ Configuracion]")
    check("settings carga y valida", test_settings_load)
    check("agent_config carga", test_agent_config_load)

    print("\n[🗄️ Base de datos]")
    check("DB SQLite inicializa", test_db_init)
    check("SqliteSaver.from_conn_string() funciona", test_sqlite_saver_init)

    print("\n[🧠 LangGraph]")
    check("ThdoraMemoryManager inicializa", test_memory_manager_init)
    check("build_thdora_graph() compila", test_build_thdora_graph)

    print("\n[🌐 Groq API — llamada real]")
    check("Groq responde correctamente", test_groq_api_call)

    print("\n[🤖 Handlers (import)]")
    check("handler nlp", test_import_handler_nlp)
    check("handler stats", test_import_handler_stats)
    check("handler diario", test_import_handler_diario)
    check("handler weather", test_import_handler_weather)
    check("handler voice", test_import_handler_voice)

    # Resumen
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = total - passed

    print("\n" + "=" * 40)
    print(f"Resultado: {passed}/{total} OK  |  {failed} FALLIDO(S)")

    if failed:
        print("\nFallos:")
        for name, ok, exc in results:
            if not ok:
                print(f"  {FAIL} {name}: {type(exc).__name__}: {exc}")
        sys.exit(1)
    else:
        print("✅ Todo OK — el bot deberia arrancar sin problemas")
        sys.exit(0)
