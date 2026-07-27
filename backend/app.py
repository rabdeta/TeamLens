from flask import Flask, jsonify

app = Flask(__name__)

EMPLOYEES = [
    {
        "id": "emp-001",
        "name": "Maya Chen",
        "role": "Software Engineer",
        "department": "Engineering",
        "responseTimeMinutes": 42,
        "meetingAttendancePercent": 96,
        "tasksCompleted": 18,
        "collaborationScore": 88,
        "summary": (
            "Consistent collaborator who completes planned work and "
            "participates reliably in team meetings."
        ),
    },
    {
        "id": "emp-002",
        "name": "Jordan Rivera",
        "role": "Product Designer",
        "department": "Design",
        "responseTimeMinutes": 35,
        "meetingAttendancePercent": 91,
        "tasksCompleted": 14,
        "collaborationScore": 93,
        "summary": (
            "Frequently collaborates across functions and maintains strong "
            "participation in scheduled work."
        ),
    },
    {
        "id": "emp-003",
        "name": "Sam Okafor",
        "role": "Engineering Manager",
        "department": "Engineering",
        "responseTimeMinutes": 58,
        "meetingAttendancePercent": 98,
        "tasksCompleted": 11,
        "collaborationScore": 90,
        "summary": (
            "Provides consistent team support and maintains dependable "
            "meeting participation across projects."
        ),
    },
]


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api/employees")
def get_employees():
    return jsonify(EMPLOYEES)


if __name__ == "__main__":
    app.run(debug=True)