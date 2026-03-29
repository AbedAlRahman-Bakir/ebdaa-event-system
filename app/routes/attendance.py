"""Attendance blueprint for QR scan check-in and attendance logs."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import AttendanceLog, User
from app.schemas import AttendanceCheckInSchema, AttendanceLogSchema

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


@attendance_bp.route("/checkin", methods=["POST"])
@jwt_required()
def checkin():
    """Scan QR code and log attendance for the day."""
    schema = AttendanceCheckInSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify(success=False, message="Validation error", errors=errors), 400

    data = schema.load(request.json)
    qr_code = data["qr_code"]
    day = data["day"]

    # Find user by QR code
    user = User.query.filter_by(qr_code=qr_code).first()
    if not user:
        return jsonify(success=False, message="Invalid QR code"), 404

    # Check for duplicate check-in
    if AttendanceLog.is_duplicate(user.id, day):
        existing = AttendanceLog.query.filter_by(user_id=user.id, day=day).first()
        return (
            jsonify(
                success=False,
                message=f"{user.name} already checked in for Day {day}",
                data={"checkin_time": existing.checkin_time.isoformat()},
            ),
            409,
        )

    # Log attendance
    log = AttendanceLog(user_id=user.id, day=day)
    db.session.add(log)
    db.session.commit()

    return (
        jsonify(
            success=True,
            message=f"Welcome, {user.name}! Day {day} check-in recorded",
            data={
                "user": user.to_dict(),
                "attendance": AttendanceLogSchema().dump(log),
            },
        ),
        201,
    )


@attendance_bp.route("", methods=["GET"])
@jwt_required()
def list_attendance():
    """List attendance logs with optional filters."""
    day = request.args.get("day", type=int)
    user_id = request.args.get("user_id", type=int)
    role = request.args.get("role")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = AttendanceLog.query

    if day:
        query = query.filter_by(day=day)
    if user_id:
        query = query.filter_by(user_id=user_id)
    if role:
        query = query.join(User).filter(User.role == role)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    logs = []
    for log in pagination.items:
        log_data = AttendanceLogSchema().dump(log)
        log_data["user_name"] = log.user.name
        log_data["user_role"] = log.user.role
        logs.append(log_data)

    return (
        jsonify(
            success=True,
            data=logs,
            total=pagination.total,
            page=page,
            per_page=per_page,
        ),
        200,
    )
