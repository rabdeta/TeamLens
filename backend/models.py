from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)
    response_time_minutes = db.Column(db.Integer, nullable=False)
    meeting_attendance_percent = db.Column(db.Integer, nullable=False)
    tasks_completed = db.Column(db.Integer, nullable=False)
    collaboration_score = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.Text, nullable=False)

    measurement_period_days = db.Column(
        db.Integer,
        nullable=False,
        default=30,
        server_default="30",
    )
    data_coverage_percent = db.Column(
        db.Integer,
        nullable=False,
        default=100,
        server_default="100",
    )
    last_synced_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "responseTimeMinutes": self.response_time_minutes,
            "meetingAttendancePercent": self.meeting_attendance_percent,
            "tasksCompleted": self.tasks_completed,
            "collaborationScore": self.collaboration_score,
            "summary": self.summary,
            "measurementPeriodDays": self.measurement_period_days,
            "dataCoveragePercent": self.data_coverage_percent,
            "lastSyncedAt": self.last_synced_at.isoformat(),
        }