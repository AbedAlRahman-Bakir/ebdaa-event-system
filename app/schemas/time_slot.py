"""Schemas for time slot serialization."""

from marshmallow import Schema, fields


class TimeSlotSchema(Schema):
    """Output schema for time slot responses."""

    id = fields.Int(dump_only=True)
    day = fields.Int()
    start_time = fields.Str()
    end_time = fields.Str()
    capacity = fields.Int()
    booked_count = fields.Int()
    available = fields.Int(dump_only=True)
