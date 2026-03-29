"""Schemas for admin user serialization and validation."""

from marshmallow import Schema, fields


class AdminUserSchema(Schema):
    """Output schema for admin user responses."""

    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    role = fields.Str()


class AdminLoginSchema(Schema):
    """Validation schema for login requests."""

    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
