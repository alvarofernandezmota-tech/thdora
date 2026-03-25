"""
Script de demostración de MemoryLifeManager.

Ejecución::

    python src/core/demo.py
"""

from datetime import date
from src.core.impl.memory_lifemanager import MemoryLifeManager


def run_demo() -> None:
    mgr = MemoryLifeManager()
    hoy = date(2026, 3, 24)

    mgr.create_appointment(hoy, "10:00", "médica", "llevar analítica")
    mgr.create_appointment(hoy, "14:00", "trabajo", "revisar roadmap")
    mgr.create_appointment(hoy, "19:00", "personal")

    mgr.log_habit(hoy, "sueno", "7h30m")
    mgr.log_habit(hoy, "THC", "0")
    mgr.log_habit(hoy, "ejercicio", "60min")
    mgr.log_habit(hoy, "agua", "2.5L")

    summary = mgr.get_day_summary(hoy)
    print(f"\n📅 Fecha: {summary['date']}")
    print(f"\n🕒 Citas ({len(summary['appointments'])})")
    for cita in summary["appointments"]:
        notes = f" ({cita['notes']})" if cita["notes"] else ""
        print(f"  {cita['time']} — {cita['type']}{notes}")
    print(f"\n📊 Hábitos")
    for habit, value in summary["habits"].items():
        print(f"  {habit}: {value}")


if __name__ == "__main__":
    run_demo()
