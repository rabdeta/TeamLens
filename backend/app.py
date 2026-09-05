import os

import secrets
from urllib.parse import urlencode
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, session
from flask_migrate import Migrate
from sqlalchemy import URL

from backend.models import DataSource, Employee, db
from backend.seed_data import DATA_SOURCE_SEED_DATA, EMPLOYEE_SEED_DATA

load_dotenv()

migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config["LINEAR_CLIENT_ID"] = os.environ["LINEAR_CLIENT_ID"]
        app.config["LINEAR_CLIENT_SECRET"] = os.environ["LINEAR_CLIENT_SECRET"]
        app.config["LINEAR_REDIRECT_URI"] = os.environ["LINEAR_REDIRECT_URI"]
        app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
        app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
            drivername="postgresql+psycopg",
            username=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            database=os.environ["DB_NAME"],
        )
    else:
        app.config.update(test_config)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/employees")
    def get_employees():
        employees = db.session.execute(
            db.select(Employee).order_by(Employee.name)
        ).scalars()

        return jsonify([employee.to_dict() for employee in employees])

    @app.get("/api/employees/<string:employee_id>")
    def get_employee(employee_id):
        employee = db.session.get(Employee, employee_id)

        if employee is None:
            return jsonify(error="Employee not found"), 404

        return jsonify(employee.to_dict())

    @app.get("/api/data-sources")
    def get_data_sources():
        data_sources = db.session.execute(
            db.select(DataSource).order_by(DataSource.display_name)
        ).scalars()

        return jsonify([source.to_dict() for source in data_sources])

    @app.get("/api/integrations/linear/connect")
    def connect_linear():
        state = secrets.token_urlsafe(32)
        session["linear_oauth_state"] = state

        query = urlencode(
            {
                "client_id": app.config["LINEAR_CLIENT_ID"],
                "redirect_uri": app.config["LINEAR_REDIRECT_URI"],
                "response_type": "code",
                "scope": "read",
                "actor": "user",
                "state": state,
            }
        )

        return redirect(f"https://linear.app/oauth/authorize?{query}")

    @app.cli.command("seed-db")
    def seed_db():
        employee_count = 0
        data_source_count = 0

        for employee_data in EMPLOYEE_SEED_DATA:
            existing_employee = db.session.get(
                Employee,
                employee_data["id"],
            )

            if existing_employee is None:
                db.session.add(Employee(**employee_data))
                employee_count += 1

        for source_data in DATA_SOURCE_SEED_DATA:
            existing_source = db.session.get(
                DataSource,
                source_data["id"],
            )

            if existing_source is None:
                db.session.add(DataSource(**source_data))
                data_source_count += 1

        db.session.add_all(
            DataSource(**source_data)
            for source_data in DATA_SOURCE_SEED_DATA
        )

        db.session.commit()

        print(
            f"Added {employee_count} employee records and "
            f"{data_source_count} data sources."
        )

    return app


if __name__ == "__main__":
    create_app().run(debug=True)

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