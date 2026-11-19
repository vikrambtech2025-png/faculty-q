def test_login_admin(client):
    r = client.post("/api/auth/login", json={"email": "admin@facultyq.com", "password": "admin123"})
    assert r.status_code == 200
    assert "admin" in r.json()["user"]["roles"]

def test_login_invalid(client):
    r = client.post("/api/auth/login", json={"email": "admin@facultyq.com", "password": "wrong"})
    assert r.status_code == 401

def test_me(client, admin_token):
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "admin@facultyq.com"

def test_unauthorized_access(client):
    r = client.get("/api/admin/dashboard")
    assert r.status_code == 401

def test_role_boundary(client, student_token):
    r = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {student_token}"})
    assert r.status_code == 403