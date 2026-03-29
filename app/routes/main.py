"""Main routes for serving HTML pages."""

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    """Serve the public landing page."""
    return render_template("landing.html")


@main_bp.route("/register")
def register():
    """Serve the visitor registration page."""
    return render_template("register.html")


@main_bp.route("/login")
def login():
    """Serve the admin login page."""
    return render_template("login.html")


@main_bp.route("/admin/dashboard")
def admin_dashboard():
    """Serve the admin dashboard page."""
    return render_template("admin/dashboard.html")


@main_bp.route("/admin/users")
def admin_users():
    """Serve the users management page."""
    return render_template("admin/users.html")


@main_bp.route("/admin/attendance")
def admin_attendance():
    """Serve the attendance logs page."""
    return render_template("admin/attendance.html")


@main_bp.route("/admin/checkin")
def admin_checkin():
    """Serve the check-in scanner page."""
    return render_template("admin/checkin.html")
