"""Visitors blueprint for public registration and admin management."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.decorators import admin_required
from app.extensions import db
from app.models import TimeSlot, Visitor
from app.schemas import TimeSlotSchema, VisitorRegistrationSchema, VisitorSchema

visitors_bp = Blueprint("visitors", __name__, url_prefix="/visitors")


@visitors_bp.route("", methods=["GET"])
@jwt_required()
@admin_required
def list_visitors():
    """List all registered visitors with optional filters."""
    day = request.args.get("day", type=int)
    visitor_type = request.args.get("type")
    time_slot_id = request.args.get("time_slot_id", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Visitor.query

    if day:
        query = query.join(TimeSlot).filter(TimeSlot.day == day)
    if visitor_type:
        query = query.filter_by(type=visitor_type)
    if time_slot_id:
        query = query.filter_by(time_slot_id=time_slot_id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return (
        jsonify(
            success=True,
            data=VisitorSchema(many=True).dump(pagination.items),
            total=pagination.total,
            page=page,
            per_page=per_page,
        ),
        200,
    )


@visitors_bp.route("/<int:visitor_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_visitor(visitor_id):
    """Get a single visitor by ID."""
    visitor = db.session.get(Visitor, visitor_id)

    if not visitor:
        return jsonify(success=False, message="Visitor not found"), 404

    return (
        jsonify(
            success=True,
            data=VisitorSchema().dump(visitor),
        ),
        200,
    )


@visitors_bp.route("/slots", methods=["GET"])
def available_slots():
    """List available time slots for visitor registration. Public endpoint."""
    slots = TimeSlot.query.all()

    return (
        jsonify(
            success=True,
            data=TimeSlotSchema(many=True).dump(slots),
        ),
        200,
    )


@visitors_bp.route("/register", methods=["POST"])
def register():
    """Public visitor registration with time slot booking."""
    schema = VisitorRegistrationSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify(success=False, message="Validation error", errors=errors), 400

    data = schema.load(request.json)

    # Find the time slot with row-level lock to prevent race conditions
    slot = db.session.query(TimeSlot).with_for_update().filter_by(id=data["time_slot_id"]).first()
    if not slot:
        return jsonify(success=False, message="Time slot not found"), 404

    # Try to book
    if not slot.book(data["group_size"]):
        return (
            jsonify(
                success=False,
                message=f"Time slot is full. Only {slot.capacity - slot.booked_count} spots remaining",
            ),
            409,
        )

    # Create visitor
    visitor = Visitor(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        city=data["city"],
        type=data["type"],
        group_size=data["group_size"],
        time_slot_id=data["time_slot_id"],
    )

    db.session.add(visitor)
    db.session.commit()

    return (
        jsonify(
            success=True,
            message="Registration successful",
            data=VisitorSchema().dump(visitor),
        ),
        201,
    )
