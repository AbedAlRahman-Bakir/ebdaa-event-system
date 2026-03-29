"""Time slot model for visitor capacity management."""

from app.extensions import db


class TimeSlot(db.Model):
    """Represents a bookable time slot with limited capacity."""

    __tablename__ = "time_slots"

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)  # 2-6
    start_time = db.Column(db.String(10), nullable=False)  # e.g. '14:00'
    end_time = db.Column(db.String(10), nullable=False)  # e.g. '16:00'
    capacity = db.Column(db.Integer, nullable=False)
    booked_count = db.Column(db.Integer, nullable=False, default=0)

    def is_available(self, group_size):
        """Check if slot has enough capacity for the group."""
        return self.booked_count + group_size <= self.capacity

    def book(self, group_size):
        """Book seats in this slot. Returns False if not enough capacity."""
        if not self.is_available(group_size):
            return False
        self.booked_count += group_size
        return True

    def to_dict(self):
        """Serialize time slot to dictionary."""
        return {
            "id": self.id,
            "day": self.day,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "capacity": self.capacity,
            "booked_count": self.booked_count,
            "available": self.capacity - self.booked_count,
        }
