"""Authentication blueprint for admin and operator login."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from app.extensions import db
from app.models import AdminUser
from app.schemas import AdminLoginSchema, AdminUserSchema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# In-memory token blacklist (use Redis in production)
blacklisted_tokens = set()


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate admin/operator and return access token."""
    schema = AdminLoginSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify(success=False, message="Validation error", errors=errors), 400

    data = schema.load(request.json)
    user = AdminUser.query.filter_by(username=data["username"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify(success=False, message="Invalid credentials"), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return (
        jsonify(
            success=True, message="Login successful", data={"access_token": token, "user": AdminUserSchema().dump(user)}
        ),
        200,
    )


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Blacklist the current access token."""
    jti = get_jwt()["jti"]
    blacklisted_tokens.add(jti)
    return jsonify(success=True, message="Logged out successfully"), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Get current authenticated user info."""
    user_id = get_jwt_identity()
    user = db.session.get(AdminUser, user_id)

    if not user:
        return jsonify(success=False, message="User not found"), 404

    return jsonify(success=True, data=AdminUserSchema().dump(user)), 200
