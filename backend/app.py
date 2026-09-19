import os

import secrets
from urllib.parse import urlencode
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, session
from flask_migrate import Migrate
from sqlalchemy import URL
from datetime import datetime, timedelta, timezone
import requests
from cryptography.fernet import Fernet, InvalidToken
from backend.models import DataSource, Employee, db
from backend.seed_data import DATA_SOURCE_SEED_DATA, EMPLOYEE_SEED_DATA
from backend.integrations.linear import (
    LinearAPIError,
    get_completed_task_counts,
    get_workspace_members,
    refresh_oauth_tokens,
)

load_dotenv()

migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config["TOKEN_ENCRYPTION_KEY"] = os.environ[
            "TOKEN_ENCRYPTION_KEY"
        ]        
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

    @app.get("/api/integrations/linear/callback")
    def linear_callback():
        authorization_code = request.args.get("code")
        returned_state = request.args.get("state")
        expected_state = session.pop("linear_oauth_state", None)

        if (
            not authorization_code
            or not returned_state
            or not expected_state
            or not secrets.compare_digest(returned_state, expected_state)
        ):
            return jsonify(error="Invalid OAuth callback"), 400

        try:
            token_response = requests.post(
                "https://api.linear.app/oauth/token",
                data={
                    "code": authorization_code,
                    "redirect_uri": app.config["LINEAR_REDIRECT_URI"],
                    "client_id": app.config["LINEAR_CLIENT_ID"],
                    "client_secret": app.config["LINEAR_CLIENT_SECRET"],
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )
            token_response.raise_for_status()
            token_data = token_response.json()
        except requests.RequestException:
            return jsonify(error="Unable to connect to Linear"), 502

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")

        if not access_token or not refresh_token or not expires_in:
            return jsonify(error="Linear returned an invalid token response"), 502

        encryption = Fernet(
            app.config["TOKEN_ENCRYPTION_KEY"].encode()
        )

        linear_source = db.session.execute(
            db.select(DataSource).where(
                DataSource.provider == "linear"
            )
        ).scalar_one_or_none()

        if linear_source is None:
            return jsonify(error="Linear data source not found"), 404

        linear_source.access_token_encrypted = encryption.encrypt(
            access_token.encode()
        ).decode()
        linear_source.refresh_token_encrypted = encryption.encrypt(
            refresh_token.encode()
        ).decode()
        linear_source.token_expires_at = (
            datetime.now(timezone.utc)
            + timedelta(seconds=int(expires_in))
        )
        linear_source.status = "connected"

        db.session.commit()

        return jsonify(status="connected", provider="linear")

    @app.get("/api/integrations/linear/members")
    def get_linear_members():
        linear_source = db.session.execute(
            db.select(DataSource).where(
                DataSource.provider == "linear"
            )
        ).scalar_one_or_none()

        if (
            linear_source is None
            or linear_source.status != "connected"
            or not linear_source.access_token_encrypted
        ):
            return jsonify(error="Linear is not connected"), 409

        encryption = Fernet(
            app.config["TOKEN_ENCRYPTION_KEY"].encode()
        )

        try:
            access_token = encryption.decrypt(
                linear_source.access_token_encrypted.encode()
            ).decode()
        except InvalidToken:
            return jsonify(error="Stored Linear token is invalid"), 500

        expires_at = linear_source.token_expires_at

        if expires_at is not None and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        token_needs_refresh = (
            expires_at is not None
            and expires_at
            <= datetime.now(timezone.utc) + timedelta(minutes=5)
        )

        if token_needs_refresh:
            if not linear_source.refresh_token_encrypted:
                return jsonify(
                    error="Linear must be reconnected"
                ), 409

            try:
                refresh_token = encryption.decrypt(
                    linear_source.refresh_token_encrypted.encode()
                ).decode()

                token_data = refresh_oauth_tokens(
                    refresh_token,
                    app.config["LINEAR_CLIENT_ID"],
                    app.config["LINEAR_CLIENT_SECRET"],
                )
            except InvalidToken:
                return jsonify(
                    error="Stored Linear token is invalid"
                ), 500
            except LinearAPIError:
                return jsonify(
                    error="Unable to refresh Linear connection"
                ), 502

            access_token = token_data["access_token"]

            linear_source.access_token_encrypted = encryption.encrypt(
                access_token.encode()
            ).decode()
            linear_source.refresh_token_encrypted = encryption.encrypt(
                token_data["refresh_token"].encode()
            ).decode()
            linear_source.token_expires_at = (
                datetime.now(timezone.utc)
                + timedelta(
                    seconds=int(token_data["expires_in"])
                )
            )

            db.session.commit()

        try:
            members = get_workspace_members(access_token)
            task_counts = get_completed_task_counts(access_token)
        except LinearAPIError:
            return jsonify(error="Unable to retrieve Linear metadata"), 502

        member_metrics = [
            {
                "id": member["id"],
                "name": member["name"],
                "active": member["active"],
                "tasksCompleted": task_counts.get(
                    member["id"],
                    0,
                ),
                "measurementPeriodDays": 30,
            }
            for member in members
        ]

        return jsonify(
            members=member_metrics,
            count=len(member_metrics),
        )
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

        

        db.session.commit()

        print(
            f"Added {employee_count} employee records and "
            f"{data_source_count} data sources."
        )

    return app


if __name__ == "__main__":
    create_app().run(debug=True)