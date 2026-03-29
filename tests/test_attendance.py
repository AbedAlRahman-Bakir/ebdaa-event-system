"""Functional tests for attendance endpoints."""


def test_checkin_success(client, auth_headers, sample_student):
    qr_code = sample_student["qr_code"]
    res = client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": qr_code,
            "day": 1,
        },
    )
    assert res.status_code == 201
    assert "Welcome" in res.get_json()["message"]


def test_checkin_duplicate(client, auth_headers, sample_student):
    qr_code = sample_student["qr_code"]

    # First check-in
    client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": qr_code,
            "day": 1,
        },
    )

    # Duplicate check-in
    res = client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": qr_code,
            "day": 1,
        },
    )
    assert res.status_code == 409
    assert "already checked in" in res.get_json()["message"]


def test_checkin_different_days(client, auth_headers, sample_student):
    qr_code = sample_student["qr_code"]

    res1 = client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": qr_code,
            "day": 1,
        },
    )
    res2 = client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": qr_code,
            "day": 2,
        },
    )
    assert res1.status_code == 201
    assert res2.status_code == 201


def test_checkin_invalid_qr(client, auth_headers):
    res = client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": "fake-qr-code",
            "day": 1,
        },
    )
    assert res.status_code == 404


def test_checkin_invalid_day(client, auth_headers, sample_student):
    res = client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": sample_student["qr_code"],
            "day": 7,
        },
    )
    assert res.status_code == 400


def test_checkin_operator_access(client, operator_headers, sample_student):
    """Operator should be able to check in users."""
    res = client.post(
        "/attendance/checkin",
        headers=operator_headers,
        json={
            "qr_code": sample_student["qr_code"],
            "day": 1,
        },
    )
    assert res.status_code == 201


def test_list_attendance(client, auth_headers, sample_student):
    qr_code = sample_student["qr_code"]
    client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": qr_code,
            "day": 1,
        },
    )
    client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": qr_code,
            "day": 2,
        },
    )

    res = client.get("/attendance", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["total"] == 2


def test_list_attendance_filter_day(client, auth_headers, sample_student):
    qr_code = sample_student["qr_code"]
    client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": qr_code,
            "day": 1,
        },
    )
    client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": qr_code,
            "day": 3,
        },
    )

    res = client.get("/attendance?day=1", headers=auth_headers)
    assert res.get_json()["total"] == 1


def test_delete_user_cascades_attendance(client, auth_headers, sample_student):
    """Deleting a user should also delete their attendance logs."""
    qr_code = sample_student["qr_code"]
    user_id = sample_student["id"]

    client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": qr_code,
            "day": 1,
        },
    )

    # Delete user
    client.delete(f"/users/{user_id}", headers=auth_headers)

    # Attendance should be empty
    res = client.get("/attendance", headers=auth_headers)
    assert res.get_json()["total"] == 0
