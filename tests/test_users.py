"""Functional tests for user endpoints."""

import io


def test_create_student(client, auth_headers):
    res = client.post(
        "/users",
        headers=auth_headers,
        json={
            "name": "Ahmed Ali",
            "role": "student",
            "extra_data": {
                "school_name": "Riyadh Academy",
                "province": "Riyadh",
                "project_name": "Smart Water",
                "project_id": "SW-001",
                "project_sector": "Technology",
            },
        },
    )
    assert res.status_code == 201
    data = res.get_json()["data"]
    assert data["name"] == "Ahmed Ali"
    assert data["qr_code"] is not None


def test_create_judge(client, auth_headers):
    res = client.post(
        "/users",
        headers=auth_headers,
        json={
            "name": "Dr. Fatima",
            "role": "judge",
            "extra_data": {
                "email": "fatima@test.com",
                "phone": "+966501234567",
                "job_title": "Professor",
            },
        },
    )
    assert res.status_code == 201


def test_create_student_missing_fields(client, auth_headers):
    res = client.post(
        "/users",
        headers=auth_headers,
        json={"name": "Ahmed", "role": "student", "extra_data": {"school_name": "Test School"}},
    )
    assert res.status_code == 400


def test_create_user_no_auth(client):
    res = client.post("/users", json={"name": "Test", "role": "student", "extra_data": {}})
    assert res.status_code == 401


def test_list_users(client, auth_headers, sample_student, sample_judge):
    res = client.get("/users", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["total"] == 2


def test_list_users_filter_role(client, auth_headers, sample_student, sample_judge):
    res = client.get("/users?role=student", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["total"] == 1


def test_list_users_search(client, auth_headers, sample_student):
    res = client.get("/users?search=Test", headers=auth_headers)
    assert res.get_json()["total"] == 1

    res = client.get("/users?search=nonexistent", headers=auth_headers)
    assert res.get_json()["total"] == 0


def test_get_user(client, auth_headers, sample_student):
    user_id = sample_student["id"]
    res = client.get(f"/users/{user_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["name"] == "Test Student"


def test_get_user_not_found(client, auth_headers):
    res = client.get("/users/999", headers=auth_headers)
    assert res.status_code == 404


def test_update_user(client, auth_headers, sample_student):
    user_id = sample_student["id"]
    res = client.put(
        f"/users/{user_id}",
        headers=auth_headers,
        json={
            "name": "Updated Name",
            "role": "student",
            "extra_data": {
                "school_name": "New School",
                "province": "Jeddah",
                "project_name": "New Project",
                "project_id": "NP-001",
                "project_sector": "Energy",
            },
        },
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["name"] == "Updated Name"


def test_delete_user(client, auth_headers, sample_student):
    user_id = sample_student["id"]
    res = client.delete(f"/users/{user_id}", headers=auth_headers)
    assert res.status_code == 200

    res = client.get(f"/users/{user_id}", headers=auth_headers)
    assert res.status_code == 404


def test_operator_cannot_access_users(client, operator_headers):
    res = client.get("/users", headers=operator_headers)
    assert res.status_code == 403


def test_bulk_import_csv(client, auth_headers):
    csv_data = "name,school_name,province,project_name,project_id,project_sector\nOmar,School A,Riyadh,Project A,PA-001,Tech\nSara,School B,Makkah,Project B,PB-002,Energy"
    data = {"file": (io.BytesIO(csv_data.encode()), "students.csv")}
    res = client.post(
        "/users/import?role=student",
        headers={
            "Authorization": auth_headers["Authorization"],
        },
        data=data,
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    result = res.get_json()
    assert result["created"] == 2
    assert result["failed"] == 0


def test_bulk_import_invalid_rows(client, auth_headers):
    csv_data = "name,school_name,province,project_name,project_id,project_sector\n,School A,Riyadh,Project A,PA-001,Tech\nSara,,Makkah,Project B,PB-002,Energy"
    data = {"file": (io.BytesIO(csv_data.encode()), "students.csv")}
    res = client.post(
        "/users/import?role=student",
        headers={
            "Authorization": auth_headers["Authorization"],
        },
        data=data,
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    result = res.get_json()
    assert result["created"] == 0
    assert result["failed"] == 2
