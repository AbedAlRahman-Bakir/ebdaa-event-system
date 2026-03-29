"""Functional tests for visitor and slot endpoints."""


def test_available_slots(client, sample_slots):
    res = client.get("/visitors/slots")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 3


def test_register_visitor(client, sample_slots):
    slot_id = sample_slots[0].id
    res = client.post(
        "/visitors/register",
        json={
            "name": "Mohammed Ali",
            "email": "mohammed@test.com",
            "phone": "+966501234567",
            "city": "Riyadh",
            "type": "parent",
            "group_size": 2,
            "time_slot_id": slot_id,
        },
    )
    assert res.status_code == 201
    assert res.get_json()["success"] is True


def test_register_visitor_invalid_email(client, sample_slots):
    res = client.post(
        "/visitors/register",
        json={
            "name": "Test",
            "email": "not-an-email",
            "phone": "+966501234567",
            "city": "Riyadh",
            "type": "student",
            "group_size": 1,
            "time_slot_id": sample_slots[0].id,
        },
    )
    assert res.status_code == 400


def test_register_visitor_invalid_type(client, sample_slots):
    res = client.post(
        "/visitors/register",
        json={
            "name": "Test",
            "email": "test@test.com",
            "phone": "+966501234567",
            "city": "Riyadh",
            "type": "alien",
            "group_size": 1,
            "time_slot_id": sample_slots[0].id,
        },
    )
    assert res.status_code == 400


def test_register_visitor_group_size_over_3(client, sample_slots):
    res = client.post(
        "/visitors/register",
        json={
            "name": "Test",
            "email": "test@test.com",
            "phone": "+966501234567",
            "city": "Riyadh",
            "type": "parent",
            "group_size": 5,
            "time_slot_id": sample_slots[0].id,
        },
    )
    assert res.status_code == 400


def test_register_visitor_slot_full(client, app, db, sample_slots):
    """Slot should reject booking when full."""
    slot = sample_slots[0]
    slot.capacity = 3
    slot.booked_count = 2
    db.session.commit()

    # group_size 2 would exceed capacity (2 + 2 = 4 > 3)
    res = client.post(
        "/visitors/register",
        json={
            "name": "Test",
            "email": "test@test.com",
            "phone": "+966501234567",
            "city": "Riyadh",
            "type": "parent",
            "group_size": 2,
            "time_slot_id": slot.id,
        },
    )
    assert res.status_code == 409


def test_register_visitor_invalid_slot(client, sample_slots):
    res = client.post(
        "/visitors/register",
        json={
            "name": "Test",
            "email": "test@test.com",
            "phone": "+966501234567",
            "city": "Riyadh",
            "type": "parent",
            "group_size": 1,
            "time_slot_id": 999,
        },
    )
    assert res.status_code == 404


def test_list_visitors_requires_auth(client, sample_slots):
    res = client.get("/visitors")
    assert res.status_code == 401


def test_list_visitors(client, auth_headers, sample_slots):
    # Register a visitor
    client.post(
        "/visitors/register",
        json={
            "name": "Test Visitor",
            "email": "visitor@test.com",
            "phone": "+966501234567",
            "city": "Riyadh",
            "type": "student",
            "group_size": 1,
            "time_slot_id": sample_slots[0].id,
        },
    )

    res = client.get("/visitors", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["total"] == 1


def test_operator_cannot_list_visitors(client, operator_headers, sample_slots):
    res = client.get("/visitors", headers=operator_headers)
    assert res.status_code == 403
