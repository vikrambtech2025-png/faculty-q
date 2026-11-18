from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from app.core.database import get_db
from app.core.deps import require_role
from app.core.security import hash_password
from app.models.user import User, Role
from app.models.faculty import FacultyProfile
from app.models.student import StudentProfile
from app.models.academic import Department, Class, Section, Semester
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/api/admin", tags=["admin"])

class CreateFaculty(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    employee_id: str
    department_id: str
    designation: str = "Assistant Professor"
    qualification: Optional[str] = None

class CreateStudent(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    roll_number: str
    class_id: str
    section_id: str
    semester_id: str

@router.get("/dashboard")
def dashboard(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    from app.models.user import User as U
    from app.models.faculty import FacultyProfile
    from app.models.student import StudentProfile
    from app.models.timetable import Timetable
    return {
        "total_faculty": db.query(FacultyProfile).count(),
        "total_students": db.query(StudentProfile).count(),
        "total_users": db.query(U).count(),
        "active_timetables": db.query(Timetable).filter(Timetable.is_active == True).count(),
    }

@router.get("/faculty")
def list_faculty(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    faculty = db.query(FacultyProfile).all()
    return [{"id": str(f.id), "employee_id": f.employee_id, "name": f.user.first_name + " " + f.user.last_name,
             "email": f.user.email, "department": f.department.name, "designation": f.designation} for f in faculty]

@router.post("/faculty")
def create_faculty(req: CreateFaculty, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "Email already registered")
    role = db.query(Role).filter(Role.name == "faculty").first()
    u = User(email=req.email, password_hash=hash_password(req.password),
             first_name=req.first_name, last_name=req.last_name)
    u.roles.append(role)
    db.add(u)
    db.flush()
    from uuid import UUID as PyUUID
    fp = FacultyProfile(user_id=u.id, employee_id=req.employee_id,
                        department_id=PyUUID(req.department_id), designation=req.designation,
                        qualification=req.qualification)
    db.add(fp)
    db.commit()
    return {"id": str(fp.id), "email": u.email, "name": u.first_name + " " + u.last_name}

@router.get("/students")
def list_students(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    students = db.query(StudentProfile).all()
    return [{"id": str(s.id), "roll_number": s.roll_number, "name": s.user.first_name + " " + s.user.last_name,
             "email": s.user.email} for s in students]

@router.post("/students")
def create_student(req: CreateStudent, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "Email already registered")
    role = db.query(Role).filter(Role.name == "student").first()
    u = User(email=req.email, password_hash=hash_password(req.password),
             first_name=req.first_name, last_name=req.last_name)
    u.roles.append(role)
    db.add(u)
    db.flush()
    from uuid import UUID as PyUUID
    sp = StudentProfile(user_id=u.id, roll_number=req.roll_number,
                        class_id=PyUUID(req.class_id), section_id=PyUUID(req.section_id), semester_id=PyUUID(req.semester_id))
    db.add(sp)
    db.commit()
    return {"id": str(sp.id), "email": u.email, "name": u.first_name + " " + u.last_name}