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
        }