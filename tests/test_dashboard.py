"""Functional tests for dashboard endpoints."""


def test_stats(client, auth_headers, sample_student, sample_judge):
    res = client.get("/dashboard/stats", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total_students"] == 1
    assert data["total_judges"] == 1


def test_attendance_data(client, auth_headers, sample_student):
    # Check in the student
    client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": sample_student["qr_code"],
            "day": 1,
        },
    )

    res = client.get("/dashboard/attendance", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "1" in data["daily"]
    assert data["daily"]["1"]["present"] == 1


def test_slots_data(client, auth_headers, sample_slots):
    res = client.get("/dashboard/slots", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "2" in data
    assert len(data["2"]) == 2


def test_checkins_counter(client, auth_headers, sample_student):
    client.post(
        "/attendance/checkin",
        headers=auth_headers,
        json={
            "qr_code": sample_student["qr_code"],
            "day": 3,
        },
    )

    res = client.get("/dashboard/checkins?day=3", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total_checked_in"] == 1


def test_checkins_missing_day(client, auth_headers):
    res = client.get("/dashboard/checkins", headers=auth_headers)
    assert res.status_code == 400


def test_dashboard_requires_admin(client, operator_headers):
    res = client.get("/dashboard/stats", headers=operator_headers)
    assert res.status_code == 403


def test_dashboard_no_auth(client):
    res = client.get("/dashboard/stats")
    assert res.status_code == 401
