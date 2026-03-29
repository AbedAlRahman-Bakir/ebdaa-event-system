"""Shared test fixtures."""

import pytest

from app import create_app
from app.extensions import db as _db
from app.models import AdminUser, TimeSlot
from config import TestingConfig


@pytest.fixture(scope="function")
def app():
    """Create a test app with in-memory SQLite database."""
    app = create_app()
    app.config.from_object(TestingConfig)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Database session."""
    return _db


@pytest.fixture
def admin_user(app, db):
    """Create and return an admin user."""
    user = AdminUser(username="testadmin", email="admin@test.com", role="admin")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def operator_user(app, db):
    """Create and return an operator user."""
    user = AdminUser(username="testoperator", email="operator@test.com", role="operator")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_token(client, admin_user):
    """Get a JWT token for admin."""
    res = client.post(
        "/auth/login",
        json={
            "username": "testadmin",
            "password": "password123",
        },
    )
    return res.get_json()["data"]["access_token"]


@pytest.fixture
def operator_token(client, operator_user):
    """Get a JWT token for operator."""
    res = client.post(
        "/auth/login",
        json={
            "username": "testoperator",
            "password": "password123",
        },
    )
    return res.get_json()["data"]["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    """Auth headers for admin."""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


@pytest.fixture
def operator_headers(operator_token):
    """Auth headers for operator."""
    return {"Authorization": f"Bearer {operator_token}", "Content-Type": "application/json"}


@pytest.fixture
def sample_student(client, auth_headers):
    """Create and return a sample student."""
    res = client.post(
        "/users",
        headers=auth_headers,
        json={
            "name": "Test Student",
            "role": "student",
            "extra_data": {
                "school_name": "Test School",
                "province": "Riyadh",
                "project_name": "Test Project",
                "project_id": "TP-001",
                "project_sector": "Technology",
            },
        },
    )
    return res.get_json()["data"]


@pytest.fixture
def sample_judge(client, auth_headers):
    """Create and return a sample judge."""
    res = client.post(
        "/users",
        headers=auth_headers,
        json={
            "name": "Test Judge",
            "role": "judge",
            "extra_data": {
                "email": "judge@test.com",
                "phone": "+966501234567",
                "job_title": "Professor",
            },
        },
    )
    return res.get_json()["data"]


@pytest.fixture
def sample_slots(app, db):
    """Create sample time slots."""
    slots = [
        TimeSlot(day=2, start_time="14:00", end_time="16:00", capacity=600),
        TimeSlot(day=2, start_time="16:00", end_time="18:00", capacity=600),
        TimeSlot(day=6, start_time="12:00", end_time="14:00", capacity=1200),
    ]
    db.session.add_all(slots)
    db.session.commit()
    return slots
