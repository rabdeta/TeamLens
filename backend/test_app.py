from backend.app import app


def test_health_endpoint():
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_employees_endpoint():
    client = app.test_client()

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