"""Dashboard blueprint for stats, attendance, and slot utilization."""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.decorators import admin_required
from app.extensions import db
from app.models import AttendanceLog, TimeSlot, User, Visitor

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
@admin_required
def stats():
    """Get overall system statistics."""
    total_students = User.query.filter_by(role="student").count()
    total_judges = User.query.filter_by(role="judge").count()
    total_visitors = Visitor.query.count()
    total_attendance_logs = AttendanceLog.query.count()

    # Visitors per day
    visitors_per_day_query = (
        db.session.query(TimeSlot.day, func.sum(Visitor.group_size))
        .join(Visitor, Visitor.time_slot_id == TimeSlot.id)
        .group_by(TimeSlot.day)
        .all()
    )
    visitors_per_day = {str(day): count for day, count in visitors_per_day_query}

    return (
        jsonify(
            success=True,
            data={
                "total_students": total_students,
                "total_judges": total_judges,
                "total_visitors": total_visitors,
                "total_attendance_logs": total_attendance_logs,
                "visitors_per_day": visitors_per_day,
            },
        ),
        200,
    )


@dashboard_bp.route("/attendance", methods=["GET"])
@jwt_required()
@admin_required
def attendance():
    """Get attendance rates and heatmap data."""
    total_users = User.query.count()

    # Daily attendance: how many checked in per day
    daily_query = db.session.query(AttendanceLog.day, func.count(AttendanceLog.id)).group_by(AttendanceLog.day).all()

    daily = {}
    total_checkins = 0
    for day, count in daily_query:
        rate = round((count / total_users) * 100, 1) if total_users > 0 else 0
        daily[str(day)] = {"present": count, "total": total_users, "rate": rate}
        total_checkins += count

    # Cumulative rate: total check-ins / (total users * 6 days)
    max_possible = total_users * 6
    cumulative_rate = round((total_checkins / max_possible) * 100, 1) if max_possible > 0 else 0

    # Heatmap: check-ins per role per day
    heatmap_query = (
        db.session.query(User.role, AttendanceLog.day, func.count(AttendanceLog.id))
        .join(AttendanceLog, AttendanceLog.user_id == User.id)
        .group_by(User.role, AttendanceLog.day)
        .all()
    )

    heatmap = {}
    for role, day, count in heatmap_query:
        if role not in heatmap:
            heatmap[role] = {}
        heatmap[role][str(day)] = count

    return (
        jsonify(
            success=True,
            data={
                "daily": daily,
                "cumulative_rate": cumulative_rate,
                "heatmap": heatmap,
            },
        ),
        200,
    )


@dashboard_bp.route("/slots", methods=["GET"])
@jwt_required()
@admin_required
def slots():
    """Get slot utilization for visitor registration."""
    all_slots = TimeSlot.query.all()

    data = {}
    for slot in all_slots:
        day_key = str(slot.day)
        if day_key not in data:
            data[day_key] = []

        data[day_key].append(
            {
                "id": slot.id,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "capacity": slot.capacity,
                "booked": slot.booked_count,
                "available": slot.capacity - slot.booked_count,
                "utilization": round((slot.booked_count / slot.capacity) * 100, 1) if slot.capacity > 0 else 0,
            }
        )

    return jsonify(success=True, data=data), 200


@dashboard_bp.route("/checkins", methods=["GET"])
@jwt_required()
@admin_required
def checkins():
    """Get real-time check-in counter for a specific day."""
    from flask import request

    day = request.args.get("day", type=int)
    if not day or day < 1 or day > 6:
        return jsonify(success=False, message="day param required (1-6)"), 400

    total_students = User.query.filter_by(role="student").count()
    total_judges = User.query.filter_by(role="judge").count()

    student_checkins = (
        db.session.query(func.count(AttendanceLog.id))
        .join(User, User.id == AttendanceLog.user_id)
        .filter(AttendanceLog.day == day, User.role == "student")
        .scalar()
    )

    judge_checkins = (
        db.session.query(func.count(AttendanceLog.id))
        .join(User, User.id == AttendanceLog.user_id)
        .filter(AttendanceLog.day == day, User.role == "judge")
        .scalar()
    )

    return (
        jsonify(
            success=True,
            data={
                "day": day,
                "students": {
                    "checked_in": student_checkins,
                    "total": total_students,
                    "remaining": total_students - student_checkins,
                },
                "judges": {
                    "checked_in": judge_checkins,
                    "total": total_judges,
                    "remaining": total_judges - judge_checkins,
                },
                "total_checked_in": student_checkins + judge_checkins,
            },
        ),
        200,
    )
