def test_list_notifications(client, admin_token):
    r = client.get("/api/notifications", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_unread_count(client, admin_token):
    r = client.get("/api/notifications/unread-count", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert "count" in r.json()

def test_mark_all_read(client, admin_token):
    r = client.put("/api/notifications/read-all", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200

def test_preferences(client, admin_token):
    r = client.get("/api/notifications/preferences", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert "email_enabled" in r.json()