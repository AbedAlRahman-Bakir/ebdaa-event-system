"""Attendance log model for daily check-in tracking."""

from datetime import UTC, datetime

from app.extensions import db


class AttendanceLog(db.Model):
    """Tracks daily attendance for participants and judges."""

    __tablename__ = "attendance_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    day = db.Column(db.Integer, nullable=False)  # 1-6
    checkin_time = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    __table_args__ = (db.UniqueConstraint("user_id", "day", name="unique_checkin_per_day"),)

    @staticmethod
    def is_duplicate(user_id, day):
        """Check if user already checked in for this day."""
        return AttendanceLog.query.filter_by(user_id=user_id, day=day).first() is not None

    def to_dict(self):
        """Serialize attendance log to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "day": self.day,
            "checkin_time": self.checkin_time.isoformat(),
        }
