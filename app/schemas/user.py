"""Schemas for user (participant/judge) serialization and validation."""

from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class StudentMetadataSchema(Schema):
    """Validation schema for student-specific metadata."""

    school_name = fields.Str(required=True, validate=validate.Length(min=2, max=150))
    province = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    project_name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    project_id = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    project_sector = fields.Str(required=True, validate=validate.Length(min=2, max=100))


class JudgeMetadataSchema(Schema):
    """Validation schema for judge-specific metadata."""

    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Length(min=7, max=20))
    job_title = fields.Str(required=True, validate=validate.Length(min=2, max=150))


class UserSchema(Schema):
    """Output schema for user responses."""

    id = fields.Int(dump_only=True)
    role = fields.Str()
    name = fields.Str()
    extra_data = fields.Dict()
    qr_code = fields.Str()
    image_url = fields.Str()


class UserImportSchema(Schema):
    """Validation schema for creating a user (participant or judge)."""

    name = fields.Str(required=True, validate=validate.Length(min=2, max=150))
    role = fields.Str(required=True, validate=validate.OneOf(["student", "judge"]))
    extra_data = fields.Dict(required=True)

    @validates_schema
    def validate_extra_data(self, data, **kwargs):
        """Validate extra_data based on user role."""
        role = data.get("role")
        extra_data = data.get("extra_data", {})

        if role == "student":
            errors = StudentMetadataSchema().validate(extra_data)
        elif role == "judge":
            errors = JudgeMetadataSchema().validate(extra_data)
        else:
            return

        if errors:
            raise ValidationError({"extra_data": errors})
