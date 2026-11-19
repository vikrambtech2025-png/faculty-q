import io

def test_today_timetable(client, faculty_token):
    r = client.get("/api/timetables/today", headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code == 200

def test_week_timetable(client, faculty_token):
    r = client.get("/api/timetables/week", headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code == 200

def test_list_timetables(client, faculty_token):
    r = client.get("/api/timetables", headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code == 200

def test_upload_csv(client, faculty_token):
    csv_content = "faculty_email,subject_code,class_name,section_name,day,period,start_time,end_time,classroom\nfaculty1@facultyq.com,DS,B.Tech CSE,A,Monday,1,09:00,09:45,101\n"
    files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    r = client.post("/api/timetables/upload", files=files, headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["timetables_created"] >= 1

def test_conflict_detection(client, faculty_token):
    csv_content = "faculty_email,subject_code,class_name,section_name,day,period,start_time,end_time,classroom\nfaculty1@facultyq.com,DS,B.Tech CSE,A,Monday,1,10:00,10:45,101\n"
    files = {"file": ("conflict.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    r = client.post("/api/timetables/upload", files=files, headers={"Authorization": f"Bearer {faculty_token}"})
    assert r.status_code == 200
    data = r.json()
    assert len(data["conflicts"]) > 0