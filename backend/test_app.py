import pytest

from backend.app import create_app
from backend.models import Employee, db
from backend.seed_data import EMPLOYEE_SEED_DATA


@pytest.fixture()
def app():
    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with test_app.app_context():
        db.create_all()

        db.session.add_all(
            Employee(**employee_data)
            for employee_data in EMPLOYEE_SEED_DATA
        )
        db.session.commit()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_employees_endpoint(client):
    response = client.get("/api/employees")
    employees = response.get_json()

    assert response.status_code == 200
    assert len(employees) == 3
    assert {employee["name"] for employee in employees} == {
        "Jordan Rivera",
        "Maya Chen",
        "Sam Okafor",
    }

    maya = next(
        employee for employee in employees if employee["name"] == "Maya Chen"
    )

    assert maya["measurementPeriodDays"] == 30
    assert maya["dataCoveragePercent"] == 100
    assert maya["lastSyncedAt"]

def test_employee_detail_endpoint(client):
    response = client.get("/api/employees/emp-001")
    employee = response.get_json()

    assert response.status_code == 200
    assert employee["name"] == "Maya Chen"
    assert employee["measurementPeriodDays"] == 30


def test_employee_detail_not_found(client):
    response = client.get("/api/employees/does-not-exist")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Employee not found"}