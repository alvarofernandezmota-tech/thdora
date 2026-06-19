#!/usr/bin/env python3
"""
Autotest de salud del ecosistema THDORA.
Ejecuta sin pytest ni dependencias externas de test.
Valida importaciones, firmas de métodos y conectividad básica.

Uso:
    python scripts/autotest.py
    python scripts/autotest.py --fast    # solo imports, sin conexión HTTP
"""
from __future__ import annotations

import asyncio
import inspect
import sys
import os
from typing import Callable

# Asegura que el PYTHONPATH incluye la raiz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

FAST_MODE = "--fast" in sys.argv

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    icon = PASS if ok else FAIL
    print(f"  {icon} {name}" + (f" — {detail}" if detail else ""))


# ════════════════════════════════════════════════════════════════
# 1. Importaciones core
# ════════════════════════════════════════════════════════════════
print("\n📦 [1/5] Verificando importaciones...")

modules_to_check = [
    ("src.bot.api_client",          "ThdoraApiClient"),
    ("src.bot.handlers.habitos",    "build_habito_handler"),
    ("src.bot.handlers.habitos",    "build_edit_hab_handler"),
    ("src.bot.handlers.citas",      "build_nueva_handler"),
    ("src.bot.handlers.citas",      "build_edit_apt_handler"),
    ("src.bot.handlers.config",     "build_config_handler"),
    ("src.bot.keyboards",           "_kb_hab_actions"),
    ("src.bot.keyboards",           "_kb_config_menu"),
    ("src.bot.utils.accum",         "_accumulate_value"),
    ("src.bot.utils.dates",         "_parse_date_arg"),
    ("src.bot.scheduler",           "schedule_user_jobs"),
    ("src.bot.main",                "main"),
]

for module_path, symbol in modules_to_check:
    try:
        mod = __import__(module_path, fromlist=[symbol])
        obj = getattr(mod, symbol, None)
        check(f"{module_path}.{symbol}", obj is not None)
    except Exception as e:
        check(f"{module_path}.{symbol}", False, str(e)[:80])


# ════════════════════════════════════════════════════════════════
# 2. Firmas de api_client — verificar que user_id está presente
# ════════════════════════════════════════════════════════════════
print("\n🔍 [2/5] Verificando firmas de ThdoraApiClient...")

try:
    from src.bot.api_client import ThdoraApiClient
    methods_needing_user_id = [
        "get_habits", "log_habit", "update_habit", "delete_habit", "get_habit_config",
        "get_habit_configs", "upsert_habit_config", "delete_habit_config",
        "get_appointments", "create_appointment", "update_appointment", "delete_appointment",
        "get_user_config", "update_user_config",
    ]
    for method_name in methods_needing_user_id:
        method = getattr(ThdoraApiClient, method_name, None)
        if method is None:
            check(f"ThdoraApiClient.{method_name} existe", False, "método no encontrado")
            continue
        sig    = inspect.signature(method)
        has_uid = "user_id" in sig.parameters
        check(f"{method_name}(user_id)", has_uid)
except Exception as e:
    check("Importar ThdoraApiClient", False, str(e))


# ════════════════════════════════════════════════════════════════
# 3. Verificar factories de handlers retornan ConversationHandler
# ════════════════════════════════════════════════════════════════
print("\n🤖 [3/5] Verificando factories de ConversationHandler...")

try:
    from telegram.ext import ConversationHandler
    from src.bot.handlers.habitos import build_habito_handler, build_edit_hab_handler
    from src.bot.handlers.citas   import build_nueva_handler, build_edit_apt_handler
    from src.bot.handlers.config  import build_config_handler

    factories = [
        ("build_habito_handler",    build_habito_handler),
        ("build_edit_hab_handler",  build_edit_hab_handler),
        ("build_nueva_handler",     build_nueva_handler),
        ("build_edit_apt_handler",  build_edit_apt_handler),
        ("build_config_handler",    build_config_handler),
    ]
    for fname, factory in factories:
        try:
            handler = factory()
            is_conv = isinstance(handler, ConversationHandler)
            check(f"{fname}() → ConversationHandler", is_conv)
        except Exception as e:
            check(f"{fname}()", False, str(e)[:80])
except Exception as e:
    check("Importar factories", False, str(e))


# ════════════════════════════════════════════════════════════════
# 4. Test de _accumulate_value inline
# ════════════════════════════════════════════════════════════════
print("\n🧮 [4/5] Verificando lógica de acumulación...")

try:
    from src.bot.utils.accum import _accumulate_value
    cases = [
        (("2", "+3"),      lambda r: "5" in str(r)),
        ((None, "+3"),     lambda r: "3" in str(r)),
        ((None, "8h"),     lambda r: r == "8h"),
        (("1L", "5L"),     lambda r: r == "5L"),  # sobreescritura
    ]
    for (existing, new_in), validator in cases:
        try:
            result = _accumulate_value(existing, new_in)
            ok = validator(result)
            check(f"accum({existing!r}, {new_in!r}) → {result!r}", ok)
        except Exception as e:
            check(f"accum({existing!r}, {new_in!r})", False, str(e)[:60])
except Exception as e:
    check("Importar _accumulate_value", False, str(e))


# ════════════════════════════════════════════════════════════════
# 5. Ping a la API (solo si no es modo --fast)
# ════════════════════════════════════════════════════════════════
print("\n🌐 [5/5] Ping a la API local...")

if FAST_MODE:
    print("  ⏭️  Saltado (modo --fast)")
else:
    async def _ping_api():
        try:
            # Configurar .env mínimo si no existe
            os.environ.setdefault("THDORA_API_URL", "http://localhost:8000")
            os.environ.setdefault("TELEGRAM_TOKEN", "dummy:test")
            os.environ.setdefault("SECRET_KEY", "test_secret_key_32chars_minimum!")

            from src.bot.api_client import ThdoraApiClient
            api = ThdoraApiClient()
            alive = await api.health()
            check("API /health responde", alive,
                  "OK" if alive else "API no disponible (normal sin Docker)")
            await ThdoraApiClient.close()
        except Exception as e:
            check("API /health", False, str(e)[:80])

    asyncio.run(_ping_api())


# ════════════════════════════════════════════════════════════════
# Resumen final
# ════════════════════════════════════════════════════════════════
total   = len(results)
passed  = sum(1 for _, ok, _ in results if ok)
failed  = total - passed

print(f"\n{'='*60}")
print(f"  Resultado: {passed}/{total} checks ✅  |  {failed} fallidos")
if failed:
    print("\n  Checks fallidos:")
    for name, ok, detail in results:
        if not ok:
            print(f"    {FAIL} {name}" + (f": {detail}" if detail else ""))
print(f"{'='*60}\n")
sys.exit(0 if failed == 0 else 1)
