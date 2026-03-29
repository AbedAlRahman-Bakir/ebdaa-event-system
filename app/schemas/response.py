"""General response wrapper schemas for consistent API responses."""

from marshmallow import Schema, fields


class SuccessResponseSchema(Schema):
    """Standard success response wrapper."""

    success = fields.Bool(dump_default=True)
    message = fields.Str()
    data = fields.Raw()


class ErrorResponseSchema(Schema):
    """Standard error response wrapper."""

    success = fields.Bool(dump_default=False)
    message = fields.Str()
    errors = fields.Dict()


class PaginatedResponseSchema(Schema):
    """Paginated response wrapper for list endpoints."""

    success = fields.Bool(dump_default=True)
    data = fields.List(fields.Raw())
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
