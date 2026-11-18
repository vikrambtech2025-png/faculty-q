from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.substitution import Substitution
from app.models.timetable import TimetableEntry
from app.models.faculty import FacultyProfile, FacultyAvailability
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/api/substitutions", tags=["substitution"])

class CreateSubstitution(BaseModel):
    timetable_entry_id: str
    substitute_faculty_id: str
    substitution_date: str
    reason: Optional[str] = None

@router.get("/available-faculty")
def available_faculty(day: int, period: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Faculty free during this day/period
    busy_ids = db.query(FacultyProfile.id).join(TimetableEntry.timetable).filter(
        TimetableEntry.day_of_week == day,
        TimetableEntry.period_number == period,
    ).all()
    busy_set = {str(b[0]) for b in busy_ids}
    all_faculty = db.query(FacultyProfile).all()
    available = [f for f in all_faculty if str(f.id) not in busy_set]
    return [{"id": str(f.id), "name": f.user.first_name + " " + f.user.last_name,
             "department": f.department.name, "designation": f.designation} for f in available]

@router.post("")
def create_substitution(req: CreateSubstitution, user=Depends(require_role("faculty", "admin")),
                       db: Session = Depends(get_db)):
    entry = db.query(TimetableEntry).filter(TimetableEntry.id == req.timetable_entry_id).first()
    if not entry:
        raise HTTPException(404, "Timetable entry not found")
    # Prevent duplicate substitution for same entry+date
    existing = db.query(Substitution).filter(
        Substitution.timetable_entry_id == req.timetable_entry_id,
        Substitution.substitution_date == req.substitution_date,
    ).first()
    if existing:
        raise HTTPException(400, "Substitution already exists for this period")
    sub = Substitution(
        timetable_entry_id=req.timetable_entry_id,
        original_faculty_id=entry.timetable.faculty_id,
        substitute_faculty_id=req.substitute_faculty_id,
        substitution_date=req.substitution_date,
        reason=req.reason,
        requested_by=user.id,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return {"id": str(sub.id), "status": sub.status}

@router.get("")
def list_substitutions(user=Depends(get_current_user), db: Session = Depends(get_db)):
    subs = db.query(Substitution).all()
    return [{"id": str(s.id), "status": s.status, "date": str(s.substitution_date),
             "original": s.original_faculty.user.first_name + " " + s.original_faculty.user.last_name,
             "substitute": s.substitute_faculty.user.first_name + " " + s.substitute_faculty.user.last_name} for s in subs]

@router.put("/{sub_id}/approve")
def approve(sub_id: str, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    sub = db.query(Substitution).filter(Substitution.id == sub_id).first()
    if not sub:
        raise HTTPException(404, "Not found")
    sub.status = "Approved"
    sub.approved_by = user.id
    db.commit()
    return {"id": str(sub.id), "status": sub.status}

@router.put("/{sub_id}/reject")
def reject(sub_id: str, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    sub = db.query(Substitution).filter(Substitution.id == sub_id).first()
    if not sub:
        raise HTTPException(404, "Not found")
    sub.status = "Rejected"
    db.commit()
    return {"id": str(sub.id), "status": sub.status}