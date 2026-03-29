"""Custom decorators for role-based access control."""

from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt


def role_required(role):
    """Restrict access to a specific role."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != role:
                return jsonify(success=False, message="Access denied"), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(fn):
    """Restrict access to admin only."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify(success=False, message="Admin access required"), 403
        return fn(*args, **kwargs)

    return wrapper
