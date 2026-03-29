"""Custom Flask CLI commands."""

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import AdminUser, TimeSlot


@click.command("seed-admin")
@with_appcontext
def seed_admin():
    """Create default admin and operator accounts."""
    admins = [
        {"username": "admin", "email": "admin@ebdaa.com", "password": "admin123", "role": "admin"},
        {"username": "operator", "email": "operator@ebdaa.com", "password": "operator123", "role": "operator"},
    ]

    for data in admins:
        if AdminUser.query.filter_by(username=data["username"]).first():
            click.echo(f"User '{data['username']}' already exists, skipping.")
            continue

        user = AdminUser(
            username=data["username"],
            email=data["email"],
            role=data["role"],
        )
        user.set_password(data["password"])
        db.session.add(user)
        click.echo(f"Created {data['role']}: {data['username']}")

    db.session.commit()
    click.echo("Done.")


@click.command("seed-slots")
@with_appcontext
def seed_slots():
    """Create predefined time slots for visitor registration."""
    if TimeSlot.query.first():
        click.echo("Time slots already exist, skipping.")
        return

    slots = []

    # Day 2-5: three 2-hour slots, 600 capacity each
    for day in range(2, 6):
        slots.append(TimeSlot(day=day, start_time="14:00", end_time="16:00", capacity=600))
        slots.append(TimeSlot(day=day, start_time="16:00", end_time="18:00", capacity=600))
        slots.append(TimeSlot(day=day, start_time="18:00", end_time="20:00", capacity=600))

    # Day 6: single slot, 1200 capacity
    slots.append(TimeSlot(day=6, start_time="12:00", end_time="14:00", capacity=1200))

    db.session.add_all(slots)
    db.session.commit()
    click.echo(f"Created {len(slots)} time slots.")
    click.echo("Done.")
