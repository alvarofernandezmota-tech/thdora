"""
Script de demostración de MemoryLifeManager.

Ejecución::

    python src/core/demo.py

Muestra un ejemplo completo del flujo de uso:
creación de citas, registro de hábitos y resumen del día.
"""

from datetime import date
from src.core.impl.memory_lifemanager import MemoryLifeManager


def run_demo() -> None:
    """Ejecuta la demostración completa del sistema."""
    mgr = MemoryLifeManager()

    hoy = date(2026, 3, 24)

    # Crear citas
    id1 = mgr.create_appointment(hoy, "10:00", "Médico", "llevar analítica")
    id2 = mgr.create_appointment(hoy, "14:00", "Reunión THEA", "revisar roadmap")
    mgr.create_appointment(hoy, "19:00", "Gym")

    # Registrar hábitos
    mgr.log_habit(hoy, "sueno", "7h30m")
    mgr.log_habit(hoy, "THC", "0")
    mgr.log_habit(hoy, "ejercicio", "60min")
    mgr.log_habit(hoy, "agua", "2.5L")

    # Mostrar resumen
    print("\n" + "=" * 50)
    print("   THDORA — Resumen del día")
    print("=" * 50)

    summary = mgr.get_day_summary(hoy)
    print(f"\n📅 Fecha: {summary['date']}")

    print(f"\n🕒 Citas ({len(summary['appointments'])})")
    for cita in summary["appointments"]:
        print(f"  {cita['time']} — {cita['type']}", end="")
        if cita["notes"]:
            print(f" ({cita['notes']})", end="")
        print()

    print(f"\n📊 Hábitos")
    for habit, value in summary["habits"].items():
        print(f"  {habit}: {value}")

    print()


if __name__ == "__main__":
    run_demo()
