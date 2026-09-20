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

class DataSource(db.Model):
    __tablename__ = "data_sources"

    id = db.Column(db.String(50), primary_key=True)
    provider = db.Column(db.String(50), nullable=False, unique=True)
    display_name = db.Column(db.String(100), nullable=False)
    status = db.Column(
        db.String(30),
        nullable=False,
        default="not_connected",
        server_default="not_connected",
    )
    last_synced_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    access_token_encrypted = db.Column(db.Text, nullable=True)
    refresh_token_encrypted = db.Column(db.Text, nullable=True)
    token_expires_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "provider": self.provider,
            "displayName": self.display_name,
            "status": self.status,
            "lastSyncedAt": (
                self.last_synced_at.isoformat()
                if self.last_synced_at
                else None
            ),
            "createdAt": self.created_at.isoformat(),
        }

class ExternalIdentity(db.Model):
    __tablename__ = "external_identities"

    id = db.Column(db.String(150), primary_key=True)
    employee_id = db.Column(
        db.String(50),
        db.ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
    )
    data_source_id = db.Column(
        db.String(50),
        db.ForeignKey("data_sources.id", ondelete="CASCADE"),
        nullable=False,
    )
    external_user_id = db.Column(
        db.String(100),
        nullable=False,
    )
    display_name = db.Column(
        db.String(120),
        nullable=False,
    )
    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    last_synced_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "data_source_id",
            "external_user_id",
            name="uq_external_identity_source_user",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "employeeId": self.employee_id,
            "dataSourceId": self.data_source_id,
            "externalUserId": self.external_user_id,
            "displayName": self.display_name,
            "active": self.active,
            "lastSyncedAt": self.last_synced_at.isoformat(),
        }