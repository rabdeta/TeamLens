import pytest

from urllib.parse import parse_qs, urlparse
from backend.app import create_app
from backend.models import DataSource, Employee, db
from backend.seed_data import DATA_SOURCE_SEED_DATA, EMPLOYEE_SEED_DATA


@pytest.fixture()
def app():
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-only-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "LINEAR_CLIENT_ID": "test-client-id",
            "LINEAR_CLIENT_SECRET": "test-client-secret",
            "LINEAR_REDIRECT_URI": "http://localhost/test-callback",
        }
    )

    with test_app.app_context():
        db.create_all()

        db.session.add_all(
            Employee(**employee_data)
            for employee_data in EMPLOYEE_SEED_DATA
        )

        db.session.add_all(
            DataSource(**source_data)
            for source_data in DATA_SOURCE_SEED_DATA
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

def test_data_sources_endpoint(client):
    response = client.get("/api/data-sources")
    data_sources = response.get_json()

    assert response.status_code == 200
    assert len(data_sources) == 4
    assert {source["provider"] for source in data_sources} == {
        "google_workspace",
        "microsoft_graph",
        "jira",
        "linear",
    }
    assert all(
        source["status"] == "not_connected"
        for source in data_sources
    )


def test_linear_connect_redirect(client):
    response = client.get("/api/integrations/linear/connect")

    assert response.status_code == 302

    query = parse_qs(urlparse(response.location).query)

    assert query["client_id"] == ["test-client-id"]
    assert query["redirect_uri"] == ["http://localhost/test-callback"]
    assert query["response_type"] == ["code"]
    assert query["scope"] == ["read"]
    assert query["actor"] == ["user"]

    with client.session_transaction() as oauth_session:
        assert query["state"] == [oauth_session["linear_oauth_state"]]