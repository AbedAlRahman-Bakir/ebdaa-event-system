"""Schemas for visitor serialization and validation."""

from marshmallow import Schema, fields, validate


class VisitorSchema(Schema):
    """Output schema for visitor responses."""

    id = fields.Int(dump_only=True)
    name = fields.Str()
    email = fields.Email()
    phone = fields.Str()
    city = fields.Str()
    type = fields.Str()
    group_size = fields.Int()
    time_slot_id = fields.Int()


class VisitorRegistrationSchema(Schema):
    """Validation schema for public visitor registration."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Length(min=7, max=20))
    city = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    type = fields.Str(required=True, validate=validate.OneOf(["student", "teacher", "parent", "other"]))
    group_size = fields.Int(required=True, validate=validate.Range(min=1, max=3))
    time_slot_id = fields.Int(required=True)
