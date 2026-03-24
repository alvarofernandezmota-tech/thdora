"""
Tests unitarios de JsonLifeManager.

Cubre:
    - Persistencia real: guardar → recargar instancia → verificar datos
    - create_appointment: creación, UUID único, validación
    - get_appointments: día con citas, día sin citas
    - delete_appointment: cita válida, IndexError, día vacío
    - log_habit: registro nuevo, sobreescritura
    - get_habits: día con hábitos, día sin hábitos
    - get_day_summary: estructura completa
    - .gitignore: datos/thdora.json no se sube al repo

Ejecución::

    pytest tests/unit/test_json_lifemanager.py -v
"""

import json
import pytest
from datetime import date
from pathlib import Path
from uuid import UUID

from src.core.impl.json_lifemanager import JsonLifeManager


@pytest.fixture
def filepath(tmp_path: Path) -> Path:
    """Fixture: fichero temporal aislado para cada test."""
    return tmp_path / "test_thdora.json"


@pytest.fixture
def mgr(filepath: Path) -> JsonLifeManager:
    """Fixture: instancia limpia apuntando al fichero temporal."""
    return JsonLifeManager(filepath=filepath)


@pytest.fixture
def hoy() -> date:
    """Fixture: fecha fija para tests reproducibles."""
    return date(2026, 3, 24)


class TestPersistencia:
    """Tests de persistencia real entre instancias."""

    def test_datos_sobreviven_al_reinicio(self, filepath: Path, hoy: date) -> None:
        """Los datos guardados deben estar disponibles en una nueva instancia."""
        mgr1 = JsonLifeManager(filepath=filepath)
        mgr1.create_appointment(hoy, "10:00", "médica", "llevar analítica")
        mgr1.log_habit(hoy, "sueno", "8h")

        mgr2 = JsonLifeManager(filepath=filepath)
        citas = mgr2.get_appointments(hoy)
        assert len(citas) == 1
        assert citas[0]["type"] == "médica"
        assert citas[0]["notes"] == "llevar analítica"
        assert mgr2.get_habits(hoy)["sueno"] == "8h"

    def test_crea_fichero_si_no_existe(self, filepath: Path) -> None:
        """El fichero JSON debe crearse al primer guardado."""
        assert not filepath.exists()
        mgr = JsonLifeManager(filepath=filepath)
        mgr.log_habit(date(2026, 3, 24), "sueno", "7h")
        assert filepath.exists()

    def test_crea_directorio_si_no_existe(self, tmp_path: Path, hoy: date) -> None:
        """El directorio padre se crea automáticamente si no existe."""
        filepath = tmp_path / "subdir" / "thdora.json"
        mgr = JsonLifeManager(filepath=filepath)
        mgr.log_habit(hoy, "agua", "2L")
        assert filepath.exists()

    def test_json_es_legible(self, filepath: Path, hoy: date) -> None:
        """El fichero JSON generado debe ser válido y parseable."""
        mgr = JsonLifeManager(filepath=filepath)
        mgr.create_appointment(hoy, "09:00", "trabajo", "sprint review")
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        assert "appointments" in data
        assert "habits" in data

    def test_multiples_dias_persisten(self, filepath: Path) -> None:
        """Los datos de múltiples días deben persistir correctamente."""
        mgr1 = JsonLifeManager(filepath=filepath)
        dia1 = date(2026, 3, 24)
        dia2 = date(2026, 3, 25)
        mgr1.create_appointment(dia1, "10:00", "médica")
        mgr1.create_appointment(dia2, "14:00", "personal")

        mgr2 = JsonLifeManager(filepath=filepath)
        assert len(mgr2.get_appointments(dia1)) == 1
        assert len(mgr2.get_appointments(dia2)) == 1


class TestCreateAppointment:
    """Tests para create_appointment()."""

    def test_retorna_uuid(self, mgr: JsonLifeManager, hoy: date) -> None:
        """El método debe devolver un UUID válido."""
        result = mgr.create_appointment(hoy, "10:00", "médica")
        assert isinstance(result, UUID)

    def test_cita_se_almacena(self, mgr: JsonLifeManager, hoy: date) -> None:
        """La cita debe aparecer al consultarla."""
        mgr.create_appointment(hoy, "10:00", "trabajo", "sprint review")
        citas = mgr.get_appointments(hoy)
        assert len(citas) == 1
        assert citas[0]["type"] == "trabajo"
        assert citas[0]["time"] == "10:00"

    def test_value_error_time_invalido(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Debe lanzar ValueError con hora en formato incorrecto."""
        with pytest.raises(ValueError, match="Formato de hora inválido"):
            mgr.create_appointment(hoy, "10h00", "médica")

    def test_value_error_type_invalido(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Debe lanzar ValueError con tipo no permitido."""
        with pytest.raises(ValueError, match="Tipo de cita inválido"):
            mgr.create_appointment(hoy, "10:00", "dentista")

    def test_no_guarda_si_falla_validacion(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Si la validación falla, no debe quedar ningún dato guardado."""
        with pytest.raises(ValueError):
            mgr.create_appointment(hoy, "INVALID", "médica")
        assert mgr.get_appointments(hoy) == []


class TestGetAppointments:
    """Tests para get_appointments()."""

    def test_dia_sin_citas_devuelve_lista_vacia(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Un día sin citas debe devolver lista vacía."""
        assert mgr.get_appointments(hoy) == []

    def test_no_mezcla_dias(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Las citas de un día no deben aparecer en otro."""
        manana = date(2026, 3, 25)
        mgr.create_appointment(hoy, "10:00", "médica")
        assert mgr.get_appointments(manana) == []


class TestDeleteAppointment:
    """Tests para delete_appointment()."""

    def test_elimina_cita_valida(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Debe eliminar la cita y persistir el cambio."""
        mgr.create_appointment(hoy, "10:00", "médica")
        result = mgr.delete_appointment(hoy, 0)
        assert result is True

        mgr_recargado = JsonLifeManager(filepath=mgr._filepath)
        assert mgr_recargado.get_appointments(hoy) == []

    def test_index_error_indice_invalido(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Debe lanzar IndexError si el índice no existe."""
        mgr.create_appointment(hoy, "10:00", "médica")
        with pytest.raises(IndexError):
            mgr.delete_appointment(hoy, 5)

    def test_index_error_dia_vacio(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Debe lanzar IndexError en un día sin citas."""
        with pytest.raises(IndexError):
            mgr.delete_appointment(hoy, 0)

    def test_index_error_indice_negativo(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Debe lanzar IndexError con índice negativo."""
        mgr.create_appointment(hoy, "10:00", "médica")
        with pytest.raises(IndexError):
            mgr.delete_appointment(hoy, -1)


class TestLogHabit:
    """Tests para log_habit()."""

    def test_registra_habito(self, mgr: JsonLifeManager, hoy: date) -> None:
        """El hábito debe quedar registrado y persistir."""
        result = mgr.log_habit(hoy, "sueno", "8h")
        assert result is True

        mgr_recargado = JsonLifeManager(filepath=mgr._filepath)
        assert mgr_recargado.get_habits(hoy)["sueno"] == "8h"

    def test_sobreescribe_valor(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Registrar el mismo hábito dos veces sobreescribe el valor."""
        mgr.log_habit(hoy, "sueno", "6h")
        mgr.log_habit(hoy, "sueno", "8h")
        assert mgr.get_habits(hoy)["sueno"] == "8h"


class TestGetHabits:
    """Tests para get_habits()."""

    def test_dia_sin_habitos_devuelve_dict_vacio(self, mgr: JsonLifeManager, hoy: date) -> None:
        """Un día sin hábitos debe devolver dict vacío."""
        assert mgr.get_habits(hoy) == {}


class TestGetDaySummary:
    """Tests para get_day_summary()."""

    def test_estructura_correcta(self, mgr: JsonLifeManager, hoy: date) -> None:
        """El resumen debe tener las claves 'date', 'appointments' y 'habits'."""
        summary = mgr.get_day_summary(hoy)
        assert "date" in summary
        assert "appointments" in summary
        assert "habits" in summary

    def test_resumen_incluye_citas_y_habitos(self, mgr: JsonLifeManager, hoy: date) -> None:
        """El resumen debe incluir los datos creados."""
        mgr.create_appointment(hoy, "10:00", "médica")
        mgr.log_habit(hoy, "sueno", "8h")
        summary = mgr.get_day_summary(hoy)
        assert len(summary["appointments"]) == 1
        assert summary["habits"]["sueno"] == "8h"


class TestGitignore:
    """Tests de configuración del repositorio."""

    def test_datos_en_gitignore(self) -> None:
        """datos/thdora.json no debe subirse al repo (.gitignore debe excluir datos/)."""
        gitignore = Path(".gitignore")
        assert gitignore.exists(), ".gitignore no encontrado en la raíz del repo"
        content = gitignore.read_text(encoding="utf-8")
        assert "datos/" in content, (
            "La carpeta datos/ no está en .gitignore — "
            "los datos personales podrían subirse al repo"
        )
