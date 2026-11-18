import uuid, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, Role
from app.models.academic import Department, AcademicYear, Semester, Subject, Class, Section, Classroom
from app.models.faculty import FacultyProfile
from app.models.student import StudentProfile
from datetime import date

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Roles
for name in ["admin", "faculty", "student"]:
    if not db.query(Role).filter(Role.name == name).first():
        db.add(Role(name=name))
db.commit()

admin_role = db.query(Role).filter(Role.name == "admin").first()
faculty_role = db.query(Role).filter(Role.name == "faculty").first()
student_role = db.query(Role).filter(Role.name == "student").first()

# Department
dept = db.query(Department).filter(Department.code == "CSE").first()
if not dept:
    dept = Department(name="Computer Science & Engineering", code="CSE", description="CSE Department")
    db.add(dept)
    db.commit()
    db.refresh(dept)

# Academic year & semester
ay = db.query(AcademicYear).filter(AcademicYear.name == "2026-2027").first()
if not ay:
    ay = AcademicYear(name="2026-2027", start_date=date(2026, 7, 1), end_date=date(2027, 6, 30))
    db.add(ay)
    db.commit()
    db.refresh(ay)

sem = db.query(Semester).filter(Semester.name == "Semester 1").first()
if not sem:
    sem = Semester(academic_year_id=ay.id, name="Semester 1", start_date=date(2026, 7, 1), end_date=date(2026, 12, 31))
    db.add(sem)
    db.commit()
    db.refresh(sem)

# Class & Section
cls = db.query(Class).filter(Class.name == "B.Tech CSE").first()
if not cls:
    cls = Class(name="B.Tech CSE", department_id=dept.id, academic_year_id=ay.id)
    db.add(cls)
    db.commit()
    db.refresh(cls)

sec = db.query(Section).filter(Section.class_id == cls.id, Section.name == "A").first()
if not sec:
    sec = Section(class_id=cls.id, name="A")
    db.add(sec)
    db.commit()
    db.refresh(sec)

# Subjects
subjects = {}
for name, code in [("Data Structures", "DS"), ("Operating Systems", "OS"), ("Database Management", "DBMS")]:
    s = db.query(Subject).filter(Subject.code == code).first()
    if not s:
        s = Subject(name=name, code=code, department_id=dept.id, credits=4)
        db.add(s)
        db.commit()
        db.refresh(s)
    subjects[code] = s

# Classrooms
for rn, fl in [("101", 1), ("102", 1), ("201", 2)]:
    c = db.query(Classroom).filter(Classroom.room_number == rn).first()
    if not c:
        db.add(Classroom(room_number=rn, floor=fl, capacity=60))
db.commit()

# Admin user
admin = db.query(User).filter(User.email == "admin@facultyq.com").first()
if not admin:
    admin = User(email="admin@facultyq.com", password_hash=hash_password("admin123"),
                 first_name="Admin", last_name="User", is_active=True, is_verified=True)
    admin.roles.append(admin_role)
    db.add(admin)
    db.commit()

# Faculty users
for i, (fn, ln, emp) in enumerate([("Alice", "Johnson", "FAC001"), ("Bob", "Smith", "FAC002")], 1):
    email = f"faculty{i}@facultyq.com"
    u = db.query(User).filter(User.email == email).first()
    if not u:
        u = User(email=email, password_hash=hash_password("faculty123"),
                 first_name=fn, last_name=ln, is_active=True, is_verified=True)
        u.roles.append(faculty_role)
        db.add(u)
        db.flush()
        fp = FacultyProfile(user_id=u.id, employee_id=emp, department_id=dept.id,
                            designation="Assistant Professor", qualification="Ph.D")
        db.add(fp)
db.commit()

# Student users
for i, (fn, ln, roll) in enumerate([("Charlie", "Brown", "STU001"), ("Diana", "Prince", "STU002"), ("Evan", "Wright", "STU003")], 1):
    email = f"student{i}@facultyq.com"
    u = db.query(User).filter(User.email == email).first()
    if not u:
        u = User(email=email, password_hash=hash_password("student123"),
                 first_name=fn, last_name=ln, is_active=True, is_verified=True)
        u.roles.append(student_role)
        db.add(u)
        db.flush()
        sp = StudentProfile(user_id=u.id, roll_number=roll, class_id=cls.id,
                            section_id=sec.id, semester_id=sem.id)
        db.add(sp)
db.commit()

print("Seed data created successfully!")
print("Admin: admin@facultyq.com / admin123")
print("Faculty: faculty1@facultyq.com / faculty123, faculty2@facultyq.com / faculty123")
print("Student: student1@facultyq.com / student123, student2@facultyq.com / student123, student3@facultyq.com / student123")
db.close()