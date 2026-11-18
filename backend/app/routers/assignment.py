from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.assignment import Assignment, Project, AssignmentSubmission
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/assignments", tags=["assignment"])

class CreateAssignment(BaseModel):
    title: str
    description: Optional[str] = None
    subject_id: str
    class_id: str
    section_id: Optional[str] = None
    deadline: str
    attachments: Optional[str] = None

@router.post("")
def create_assignment(req: CreateAssignment, user=Depends(require_role("faculty", "admin")),
                     db: Session = Depends(get_db)):
    from app.models.faculty import FacultyProfile
    fp = db.query(FacultyProfile).filter(FacultyProfile.user_id == user.id).first()
    if not fp:
        raise HTTPException(400, "Faculty profile not found")
    a = Assignment(
        title=req.title, description=req.description, subject_id=req.subject_id,
        class_id=req.class_id, section_id=req.section_id, faculty_id=fp.id,
        deadline=req.deadline, attachments=req.attachments,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"id": str(a.id), "title": a.title, "deadline": str(a.deadline)}

@router.get("")
def list_assignments(user=Depends(get_current_user), db: Session = Depends(get_db)):
    assignments = db.query(Assignment).filter(Assignment.is_cancelled == False).all()
    return [{"id": str(a.id), "title": a.title, "subject": a.subject.name,
             "deadline": str(a.deadline), "faculty": a.faculty.user.first_name + " " + a.faculty.user.last_name,
             "class": a.class_.name} for a in assignments]

@router.get("/student")
def student_assignments(user=Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.student import StudentProfile
    sp = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not sp:
        raise HTTPException(400, "Student profile not found")
    assignments = db.query(Assignment).filter(
        Assignment.class_id == sp.class_id,
        Assignment.is_cancelled == False,
    ).all()
    result = []
    for a in assignments:
        sub = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == a.id,
            AssignmentSubmission.student_id == sp.id,
        ).first()
        result.append({
            "id": str(a.id), "title": a.title, "subject": a.subject.name,
            "deadline": str(a.deadline), "faculty": a.faculty.user.first_name + " " + a.faculty.user.last_name,
            "status": sub.status if sub else "Pending",
        })
    return result

@router.put("/{aid}")
def update_assignment(aid: str, req: CreateAssignment, user=Depends(require_role("faculty", "admin")),
                      db: Session = Depends(get_db)):
    a = db.query(Assignment).filter(Assignment.id == aid).first()
    if not a:
        raise HTTPException(404, "Not found")
    a.title = req.title
    a.description = req.description
    a.deadline = req.deadline
    a.attachments = req.attachments
    db.commit()
    return {"id": str(a.id), "title": a.title}

@router.delete("/{aid}")
def delete_assignment(aid: str, user=Depends(require_role("faculty", "admin")), db: Session = Depends(get_db)):
    a = db.query(Assignment).filter(Assignment.id == aid).first()
    if not a:
        raise HTTPException(404, "Not found")
    a.is_cancelled = True
    db.commit()
    return {"message": "Assignment cancelled"}

# Projects
@router.post("/projects")
def create_project(req: CreateAssignment, user=Depends(require_role("faculty", "admin")), db: Session = Depends(get_db)):
    from app.models.faculty import FacultyProfile
    fp = db.query(FacultyProfile).filter(FacultyProfile.user_id == user.id).first()
    if not fp:
        raise HTTPException(400, "Faculty profile not found")
    p = Project(title=req.title, description=req.description, subject_id=req.subject_id,
                class_id=req.class_id, faculty_id=fp.id, deadline=req.deadline, attachments=req.attachments)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": str(p.id), "title": p.title}

@router.get("/projects")
def list_projects(user=Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.is_cancelled == False).all()
    return [{"id": str(p.id), "title": p.title, "subject": p.subject.name,
             "deadline": str(p.deadline)} for p in projects]