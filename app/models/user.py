"""User model for participants (students) and judges."""

import hashlib
import hmac
import uuid

from flask import current_app

from app.extensions import db


class User(db.Model):
    """Represents both students and judges, differentiated by role."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(10), nullable=False)  # 'student' or 'judge'
    name = db.Column(db.String(150), nullable=False)
    extra_data = db.Column(db.JSON, default=dict)
    qr_code = db.Column(db.String(200), unique=True)
    image_url = db.Column(db.String(300))

    attendance_logs = db.relationship("AttendanceLog", backref="user", lazy=True, cascade="all, delete-orphan")

    def generate_qr_code(self):
        """Generate a signed UUID-based QR code for this user."""
        raw = str(uuid.uuid4())
        secret = current_app.config.get("QR_SECRET", "")
        signature = hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()[:12]
        self.qr_code = f"{raw}:{signature}"
        return self.qr_code

    def to_dict(self):
        """Serialize user to dictionary."""
        return {
            "id": self.id,
            "role": self.role,
            "name": self.name,
            "extra_data": self.extra_data,
            "qr_code": self.qr_code,
            "image_url": self.image_url,
        }
