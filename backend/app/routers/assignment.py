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
    from uuid import UUID as PyUUID
    from datetime import datetime as dt
    deadline = dt.fromisoformat(req.deadline.replace('Z', '+00:00')).replace(tzinfo=None) if 'T' in req.deadline else dt.strptime(req.deadline, '%Y-%m-%d %H:%M:%S')
    a = Assignment(
        title=req.title, description=req.description,
        subject_id=PyUUID(req.subject_id),
        class_id=PyUUID(req.class_id),
        section_id=PyUUID(req.section_id) if req.section_id else None,
        faculty_id=fp.id,
        deadline=deadline, attachments=req.attachments,
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
    now = datetime.utcnow()
    for a in assignments:
        sub = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == a.id,
            AssignmentSubmission.student_id == sp.id,
        ).first()
        status = sub.status if sub else "Pending"
        # Auto-mark overdue
        if status == "Pending" and a.deadline < now:
            status = "Overdue"
        result.append({
            "id": str(a.id), "title": a.title, "subject": a.subject.name,
            "deadline": str(a.deadline), "faculty": a.faculty.user.first_name + " " + a.faculty.user.last_name,
            "status": status,
        })
    return result

@router.post("/{aid}/submit")
def submit_assignment(aid: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.student import StudentProfile
    sp = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not sp:
        raise HTTPException(400, "Student profile not found")
    from uuid import UUID as PyUUID
    a = db.query(Assignment).filter(Assignment.id == PyUUID(aid)).first()
    if not a:
        raise HTTPException(404, "Assignment not found")
    from uuid import UUID as PyUUID
    sub = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == PyUUID(aid),
        AssignmentSubmission.student_id == PyUUID(str(sp.id)),
    ).first()
    if not sub:
        from uuid import UUID as PyUUID
        sub = AssignmentSubmission(assignment_id=PyUUID(aid), student_id=PyUUID(str(sp.id)))
        db.add(sub)
    sub.status = "Submitted"
    sub.submitted_at = datetime.utcnow()
    db.commit()
    return {"id": str(sub.id), "status": sub.status, "submitted_at": str(sub.submitted_at)}

@router.get("/{aid}/submissions")
def list_submissions(aid: str, user=Depends(require_role("faculty", "admin")), db: Session = Depends(get_db)):
    from uuid import UUID as PyUUID
    subs = db.query(AssignmentSubmission).filter(AssignmentSubmission.assignment_id == PyUUID(aid)).all()
    return [{"id": str(s.id), "student": s.student.user.first_name + " " + s.student.user.last_name,
             "roll": s.student.roll_number, "status": s.status,
             "submitted_at": str(s.submitted_at) if s.submitted_at else None,
             "grade": s.grade} for s in subs]

@router.put("/submissions/{sid}/grade")
def grade_submission(sid: str, grade: str, feedback: str = None,
                     user=Depends(require_role("faculty", "admin")), db: Session = Depends(get_db)):
    from uuid import UUID as PyUUID
    sub = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == PyUUID(sid)).first()
    if not sub:
        raise HTTPException(404, "Not found")
    sub.grade = grade
    sub.feedback = feedback
    sub.status = "Completed"
    db.commit()
    return {"id": str(sub.id), "grade": sub.grade, "status": sub.status}

@router.put("/{aid}")
def update_assignment(aid: str, req: CreateAssignment, user=Depends(require_role("faculty", "admin")),
                      db: Session = Depends(get_db)):
    from uuid import UUID as PyUUID
    a = db.query(Assignment).filter(Assignment.id == PyUUID(aid)).first()
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
    from uuid import UUID as PyUUID
    a = db.query(Assignment).filter(Assignment.id == PyUUID(aid)).first()
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
    from uuid import UUID as PyUUID
    from datetime import datetime as dt
    deadline = dt.fromisoformat(req.deadline.replace('Z', '+00:00')).replace(tzinfo=None) if 'T' in req.deadline else dt.strptime(req.deadline, '%Y-%m-%d %H:%M:%S')
    p = Project(title=req.title, description=req.description, subject_id=PyUUID(req.subject_id),
                class_id=PyUUID(req.class_id), faculty_id=fp.id, deadline=deadline, attachments=req.attachments)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": str(p.id), "title": p.title}

@router.get("/projects")
def list_projects(user=Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.is_cancelled == False).all()
    return [{"id": str(p.id), "title": p.title, "subject": p.subject.name,
             "deadline": str(p.deadline)} for p in projects]