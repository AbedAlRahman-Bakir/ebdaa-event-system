"""Schemas for attendance log serialization and validation."""

from marshmallow import Schema, fields, validate


class AttendanceLogSchema(Schema):
    """Output schema for attendance log responses."""

    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    day = fields.Int()
    checkin_time = fields.DateTime()


class AttendanceCheckInSchema(Schema):
    """Validation schema for QR scan check-in requests."""

    qr_code = fields.Str(required=True)
    day = fields.Int(required=True, validate=validate.Range(min=1, max=6))
