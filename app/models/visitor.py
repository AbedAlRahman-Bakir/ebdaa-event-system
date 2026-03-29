"""Visitor model for public registration."""

from app.extensions import db


class Visitor(db.Model):
    """Represents a visitor who registers via the public landing page."""

    __tablename__ = "visitors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # student, teacher, parent, other
    group_size = db.Column(db.Integer, nullable=False, default=1)  # 1-3
    time_slot_id = db.Column(db.Integer, db.ForeignKey("time_slots.id"), nullable=False)

    time_slot = db.relationship("TimeSlot", backref="visitors")

    def to_dict(self):
        """Serialize visitor to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
            "type": self.type,
            "group_size": self.group_size,
            "time_slot_id": self.time_slot_id,
        }
