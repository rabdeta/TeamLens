import os

from flask import Flask, jsonify
from dotenv import load_dotenv
from sqlalchemy import URL

from backend.models import Employee, db
from backend.seed_data import EMPLOYEE_SEED_DATA

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api/employees")
def get_employees():
    employees = db.session.execute(
        db.select(Employee).order_by(Employee.name)
    ).scalars()

    return jsonify([employee.to_dict() for employee in employees])


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Database tables created.")

@app.cli.command("seed-db")
def seed_db():
    added_count = 0

    for employee_data in EMPLOYEE_SEED_DATA:
        existing_employee = db.session.get(Employee, employee_data["id"])

        if existing_employee is None:
            db.session.add(Employee(**employee_data))
            added_count += 1

    db.session.commit()
    print(f"Added {added_count} employee records.")

if __name__ == "__main__":
    app.run(debug=True)