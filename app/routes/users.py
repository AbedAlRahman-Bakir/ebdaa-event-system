"""Users blueprint for participants and judges management."""

import csv
import io

import pandas as pd
import qrcode
from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.decorators import admin_required
from app.extensions import db
from app.models import User
from app.schemas import UserImportSchema, UserSchema
from app.schemas.user import JudgeMetadataSchema, StudentMetadataSchema

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    """List all users with optional filters."""
    role = request.args.get("role")
    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = User.query

    if role:
        query = query.filter_by(role=role)
    if search:
        query = query.filter(User.name.ilike(f"%{search}%"))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return (
        jsonify(
            success=True,
            data=UserSchema(many=True).dump(pagination.items),
            total=pagination.total,
            page=page,
            per_page=per_page,
        ),
        200,
    )


@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_user(user_id):
    """Get a single user by ID."""
    user = db.session.get(User, user_id)

    if not user:
        return jsonify(success=False, message="User not found"), 404

    return (
        jsonify(
            success=True,
            data=UserSchema().dump(user),
        ),
        200,
    )


@users_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_user():
    """Create a single participant or judge."""
    schema = UserImportSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify(success=False, message="Validation error", errors=errors), 400

    data = schema.load(request.json)

    user = User(
        name=data["name"],
        role=data["role"],
        extra_data=data.get("extra_data", {}),
    )
    user.generate_qr_code()

    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            success=True,
            message="User created successfully",
            data=UserSchema().dump(user),
        ),
        201,
    )


@users_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_user(user_id):
    """Update an existing participant or judge."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404

    schema = UserImportSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify(success=False, message="Validation error", errors=errors), 400

    data = schema.load(request.json)

    user.name = data["name"]
    user.role = data["role"]
    user.extra_data = data["extra_data"]

    db.session.commit()

    return (
        jsonify(
            success=True,
            message="User updated successfully",
            data=UserSchema().dump(user),
        ),
        200,
    )


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Delete a participant or judge."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404

    db.session.delete(user)
    db.session.commit()

    return (
        jsonify(
            success=True,
            message="User deleted successfully",
        ),
        200,
    )


STUDENT_COLUMNS = ["name", "school_name", "province", "project_name", "project_id", "project_sector"]
JUDGE_COLUMNS = ["name", "email", "phone", "job_title"]


@users_bp.route("/import", methods=["POST"])
@jwt_required()
@admin_required
def import_users():
    """Bulk import users from CSV or Excel file."""
    role = request.args.get("role")
    if role not in ("student", "judge"):
        return jsonify(success=False, message="role query param required (student or judge)"), 400

    file = request.files.get("file")
    if not file:
        return jsonify(success=False, message="No file uploaded"), 400

    filename = file.filename.lower()
    if filename.endswith(".csv"):
        df = pd.read_csv(file, keep_default_na=False)
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file, keep_default_na=False)
    else:
        return jsonify(success=False, message="Only CSV and Excel files are supported"), 400

    expected = STUDENT_COLUMNS if role == "student" else JUDGE_COLUMNS
    missing = [col for col in expected if col not in df.columns]
    if missing:
        return jsonify(success=False, message=f'Missing columns: {", ".join(missing)}'), 400

    metadata_schema = StudentMetadataSchema() if role == "student" else JudgeMetadataSchema()
    metadata_fields = [col for col in expected if col != "name"]

    created = 0
    failed = 0
    errors = []

    for index, row in df.iterrows():
        row_data = row.to_dict()
        row_num = index + 2  # +2 because index starts at 0 and row 1 is header

        name = str(row_data.get("name", "")).strip()
        if not name:
            failed += 1
            errors.append({"row": row_num, "errors": {"name": "Name is required"}})
            continue

        extra_data = {field: str(row_data.get(field, "")).strip() for field in metadata_fields}
        validation_errors = metadata_schema.validate(extra_data)
        if validation_errors:
            failed += 1
            errors.append({"row": row_num, "errors": validation_errors})
            continue

        user = User(name=name, role=role, extra_data=extra_data)
        user.generate_qr_code()
        db.session.add(user)
        created += 1

    db.session.commit()

    return (
        jsonify(
            success=True,
            message="Import completed",
            created=created,
            failed=failed,
            errors=errors,
        ),
        200,
    )


def _draw_badge(c, user):
    """Draw a single badge on the current PDF page."""
    from reportlab.lib.utils import ImageReader

    width, height = A6
    extra = user.extra_data or {}
    organization = extra.get("school_name", "") if user.role == "student" else extra.get("job_title", "")

    # QR code image
    qr_img = qrcode.make(user.qr_code)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # Badge border
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.rect(5 * mm, 5 * mm, width - 10 * mm, height - 10 * mm)

    # Event title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 20 * mm, "Ebdaa Event")

    # Role label
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, height - 30 * mm, user.role.upper())

    # User name
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width / 2, height - 45 * mm, user.name)

    # Organization
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 53 * mm, organization)

    # QR code
    qr_reader = ImageReader(qr_buffer)
    qr_size = 35 * mm
    c.drawImage(qr_reader, (width - qr_size) / 2, 15 * mm, qr_size, qr_size)

    # User ID
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 10 * mm, f"ID: {user.id}")


@users_bp.route("/<int:user_id>/badge", methods=["GET"])
@jwt_required()
@admin_required
def generate_badge(user_id):
    """Generate a printable PDF badge for a single user."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A6)
    _draw_badge(c, user)
    c.save()
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f'badge_{user.name.replace(" ", "_")}_{user.id}.pdf',
    )


@users_bp.route("/badges", methods=["GET"])
@jwt_required()
@admin_required
def generate_badges_bulk():
    """Generate a PDF with badges for all users of a given role."""
    role = request.args.get("role")
    if role not in ("student", "judge"):
        return jsonify(success=False, message="role query param required (student or judge)"), 400

    users = User.query.filter_by(role=role).all()
    if not users:
        return jsonify(success=False, message=f"No {role}s found"), 404

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A6)

    for i, user in enumerate(users):
        _draw_badge(c, user)
        if i < len(users) - 1:
            c.showPage()

    c.save()
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"badges_{role}s.pdf",
    )


@users_bp.route("/export", methods=["GET"])
@jwt_required()
@admin_required
def export_contacts():
    """Export user contacts as a CSV file."""
    role = request.args.get("role")
    if role not in ("student", "judge"):
        return jsonify(success=False, message="role query param required (student or judge)"), 400

    users = User.query.filter_by(role=role).all()
    if not users:
        return jsonify(success=False, message=f"No {role}s found"), 404

    output = io.StringIO()
    writer = csv.writer(output)

    if role == "judge":
        writer.writerow(["Name", "Email", "Phone", "Job Title"])
        for user in users:
            extra = user.extra_data or {}
            writer.writerow([user.name, extra.get("email", ""), extra.get("phone", ""), extra.get("job_title", "")])
    else:
        writer.writerow(["Name", "School Name", "Province", "Project Name", "Project ID", "Project Sector"])
        for user in users:
            extra = user.extra_data or {}
            writer.writerow(
                [
                    user.name,
                    extra.get("school_name", ""),
                    extra.get("province", ""),
                    extra.get("project_name", ""),
                    extra.get("project_id", ""),
                    extra.get("project_sector", ""),
                ]
            )

    csv_buffer = io.BytesIO(output.getvalue().encode("utf-8"))

    return send_file(
        csv_buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{role}s_contacts.csv",
    )
