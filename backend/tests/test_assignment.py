from datetime import datetime, timedelta

def test_create_assignment(client, faculty_token):
    # Get subject and class ids
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.core.database import SessionLocal
    from app.models.academic import Subject, Class, Section
    db = SessionLocal()
    subj = db.query(Subject).first()
    cls = db.query(Class).first()
    sec = db.query(Section).first()
    db.close()
    deadline = (datetime.utcnow() + timedelta(hours=25)).isoformat()
    payload = {
        "title": "Test Assignment",
        "description": "Test desc",
        "subject_id": str(subj.id),
        "class_id": str(cls.id),
        "section_id": str(sec.id),
        "deadline": deadline,
    }
    r = client.post("/api/assignments", json=payload, headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code == 200
    assert r.json()["title"] == "Test Assignment"

def test_student_view_assignments(client, student_token):
    r = client.get("/api/assignments/student", headers={"Authorization": f"Bearer {student_token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_list_assignments(client, faculty_token):
    r = client.get("/api/assignments", headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_cancel_assignment(client, faculty_token):
    # Create one first
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.core.database import SessionLocal
    from app.models.academic import Subject, Class, Section
    from datetime import datetime, timedelta
    db = SessionLocal()
    subj = db.query(Subject).first()
    cls = db.query(Class).first()
    sec = db.query(Section).first()
    db.close()
    deadline = (datetime.utcnow() + timedelta(hours=25)).isoformat()
    payload = {"title": "To Cancel", "subject_id": str(subj.id), "class_id": str(cls.id),
               "section_id": str(sec.id), "deadline": deadline}
    r = client.post("/api/assignments", json=payload, headers={"Authorization": f"Bearer {faculty_token}"})
    aid = r.json()["id"]
    r = client.delete(f"/api/assignments/{aid}", headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code == 200
    assert r.json()["message"] == "Assignment cancelled"