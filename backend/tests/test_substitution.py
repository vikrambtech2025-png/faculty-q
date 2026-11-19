def test_available_faculty(client, faculty_token):
    r = client.get("/api/substitutions/available-faculty?day=0&period=1", headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_list_substitutions(client, faculty_token):
    r = client.get("/api/substitutions", headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_admin_approve_requires_admin(client, faculty_token):
    # Faculty cannot approve
    r = client.put("/api/substitutions/00000000-0000-0000-0000-000000000000/approve", headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code in (403, 404)