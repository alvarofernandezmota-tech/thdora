"""
Tests de integración de la API REST de THDORA.

Usa TestClient de FastAPI para testear los endpoints completos:
    - POST   /appointments/{date}
    - GET    /appointments/{date}
    - DELETE /appointments/{date}/{index}
    - POST   /habits/{date}
    - GET    /habits/{date}
    - GET    /  (health check)

Ejecución::

    pytest tests/integration/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from src.api.main import app, get_manager
from src.core.impl.json_lifemanager import JsonLifeManager


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    """
    Fixture: TestClient con JsonLifeManager apuntando a fichero temporal.

    Sobreescribe la dependencia para aislar los tests del fichero real.
    """
    test_manager = JsonLifeManager(filepath=tmp_path / "test_thdora.json")
    app.dependency_overrides[JsonLifeManager] = lambda: test_manager
    yield TestClient(app)
    app.dependency_overrides.clear()


DATE = "2026-03-24"
VALID_APPOINTMENT = {"time": "10:00", "type": "médica", "notes": "llevar analítica"}


class TestHealthCheck:
    """Tests del endpoint de health check."""

    def test_health_ok(self, client: TestClient) -> None:
        """Debe devolver status ok."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestCreateAppointment:
    """Tests de POST /appointments/{date}."""

    def test_crea_cita_valida(self, client: TestClient) -> None:
        """Debe crear la cita y devolver su ID con status 201."""
        response = client.post(f"/appointments/{DATE}", json=VALID_APPOINTMENT)
        assert response.status_code == 201
        assert "id" in response.json()

    def test_error_tipo_invalido(self, client: TestClient) -> None:
        """Debe devolver 422 con tipo de cita no permitido."""
        response = client.post(
            f"/appointments/{DATE}", json={"time": "10:00", "type": "dentista"}
        )
        assert response.status_code == 422

    def test_error_hora_invalida(self, client: TestClient) -> None:
        """Debe devolver 422 con formato de hora incorrecto."""
        response = client.post(
            f"/appointments/{DATE}", json={"time": "10h00", "type": "médica"}
        )
        assert response.status_code == 422

    def test_error_fecha_invalida(self, client: TestClient) -> None:
        """Debe devolver 422 con fecha en formato incorrecto."""
        response = client.post("/appointments/not-a-date", json=VALID_APPOINTMENT)
        assert response.status_code == 422


class TestGetAppointments:
    """Tests de GET /appointments/{date}."""

    def test_devuelve_lista_vacia(self, client: TestClient) -> None:
        """Un día sin citas debe devolver lista vacía con status 200."""
        response = client.get(f"/appointments/{DATE}")
        assert response.status_code == 200
        assert response.json() == []

    def test_devuelve_citas_creadas(self, client: TestClient) -> None:
        """Debe devolver las citas del día correctamente."""
        client.post(f"/appointments/{DATE}", json=VALID_APPOINTMENT)
        response = client.get(f"/appointments/{DATE}")
        assert response.status_code == 200
        citas = response.json()
        assert len(citas) == 1
        assert citas[0]["type"] == "médica"
        assert citas[0]["time"] == "10:00"

    def test_devuelve_multiples_citas(self, client: TestClient) -> None:
        """Debe devolver todas las citas del día."""
        client.post(f"/appointments/{DATE}", json=VALID_APPOINTMENT)
        client.post(
            f"/appointments/{DATE}", json={"time": "14:00", "type": "trabajo"}
        )
        response = client.get(f"/appointments/{DATE}")
        assert len(response.json()) == 2

    def test_no_mezcla_dias(self, client: TestClient) -> None:
        """Las citas de un día no deben aparecer en otro."""
        client.post(f"/appointments/{DATE}", json=VALID_APPOINTMENT)
        response = client.get("/appointments/2026-03-25")
        assert response.json() == []


class TestDeleteAppointment:
    """Tests de DELETE /appointments/{date}/{index}."""

    def test_elimina_cita_existente(self, client: TestClient) -> None:
        """Debe eliminar la cita y devolver 204."""
        client.post(f"/appointments/{DATE}", json=VALID_APPOINTMENT)
        response = client.delete(f"/appointments/{DATE}/0")
        assert response.status_code == 204

        citas = client.get(f"/appointments/{DATE}").json()
        assert citas == []

    def test_error_indice_invalido(self, client: TestClient) -> None:
        """Debe devolver 404 si el índice no existe."""
        client.post(f"/appointments/{DATE}", json=VALID_APPOINTMENT)
        response = client.delete(f"/appointments/{DATE}/99")
        assert response.status_code == 404

    def test_error_dia_vacio(self, client: TestClient) -> None:
        """Debe devolver 404 al intentar eliminar en un día sin citas."""
        response = client.delete(f"/appointments/{DATE}/0")
        assert response.status_code == 404


class TestLogHabit:
    """Tests de POST /habits/{date}."""

    def test_registra_habito(self, client: TestClient) -> None:
        """Debe registrar el hábito y devolver 201."""
        response = client.post(
            f"/habits/{DATE}", json={"habit": "sueno", "value": "8h"}
        )
        assert response.status_code == 201
        assert response.json()["habit"] == "sueno"
        assert response.json()["value"] == "8h"

    def test_error_fecha_invalida(self, client: TestClient) -> None:
        """Debe devolver 422 con fecha en formato incorrecto."""
        response = client.post(
            "/habits/not-a-date", json={"habit": "sueno", "value": "8h"}
        )
        assert response.status_code == 422


class TestGetHabits:
    """Tests de GET /habits/{date}."""

    def test_devuelve_lista_vacia(self, client: TestClient) -> None:
        """Un día sin hábitos debe devolver lista vacía con status 200."""
        response = client.get(f"/habits/{DATE}")
        assert response.status_code == 200
        assert response.json() == []

    def test_devuelve_habitos_registrados(self, client: TestClient) -> None:
        """Debe devolver los hábitos del día correctamente."""
        client.post(f"/habits/{DATE}", json={"habit": "sueno", "value": "8h"})
        client.post(f"/habits/{DATE}", json={"habit": "THC", "value": "0"})
        response = client.get(f"/habits/{DATE}")
        assert response.status_code == 200
        habitos = {h["habit"]: h["value"] for h in response.json()}
        assert habitos["sueno"] == "8h"
        assert habitos["THC"] == "0"
