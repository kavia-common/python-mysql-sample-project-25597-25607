from __future__ import annotations


def test_list_users_initially_empty(app_client):
    resp = app_client.get("/api/users/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_user_and_get_by_id(app_client):
    create = app_client.post(
        "/api/users/",
        json={"name": "Test User", "email": "test@example.com"},
    )
    assert create.status_code == 201
    created = create.get_json()
    assert created["id"] >= 1
    assert created["name"] == "Test User"
    assert created["email"] == "test@example.com"
    assert "created_at" in created

    get_one = app_client.get(f"/api/users/{created['id']}")
    assert get_one.status_code == 200
    assert get_one.get_json()["email"] == "test@example.com"


def test_create_user_requires_valid_email(app_client):
    resp = app_client.post("/api/users/", json={"name": "Bad", "email": "not-an-email"})
    # flask-smorest/marshmallow will reject payload
    assert resp.status_code in (400, 422)


def test_email_uniqueness_conflict(app_client):
    r1 = app_client.post("/api/users/", json={"name": "A", "email": "dup@example.com"})
    assert r1.status_code == 201

    r2 = app_client.post("/api/users/", json={"name": "B", "email": "dup@example.com"})
    assert r2.status_code == 409


def test_patch_user(app_client):
    created = app_client.post("/api/users/", json={"name": "Old", "email": "old@example.com"}).get_json()

    resp = app_client.patch(f"/api/users/{created['id']}", json={"name": "New"})
    assert resp.status_code == 200
    updated = resp.get_json()
    assert updated["name"] == "New"
    assert updated["email"] == "old@example.com"


def test_put_requires_both_fields(app_client):
    created = app_client.post("/api/users/", json={"name": "X", "email": "x@example.com"}).get_json()

    resp = app_client.put(f"/api/users/{created['id']}", json={"name": "OnlyName"})
    assert resp.status_code == 400


def test_delete_user(app_client):
    created = app_client.post("/api/users/", json={"name": "Del", "email": "del@example.com"}).get_json()

    del_resp = app_client.delete(f"/api/users/{created['id']}")
    assert del_resp.status_code == 204

    get_resp = app_client.get(f"/api/users/{created['id']}")
    assert get_resp.status_code == 404


def test_get_missing_user_404(app_client):
    resp = app_client.get("/api/users/999999")
    assert resp.status_code == 404
