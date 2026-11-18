from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.timetable import Timetable, TimetableEntry
from app.models.academic import Subject, Class, Section, Classroom
from app.models.faculty import FacultyProfile
from datetime import date, timedelta
from typing import List
import csv, io, uuid

router = APIRouter(prefix="/api/timetables", tags=["timetable"])

@router.get("")
def list_timetables(user=Depends(get_current_user), db: Session = Depends(get_db)):
    tts = db.query(Timetable).filter(Timetable.is_active == True).all()
    return [{"id": str(t.id), "faculty": t.faculty.user.first_name + " " + t.faculty.user.last_name,
             "subject": t.subject.name, "class": t.class_.name, "section": t.section.name,
             "start_date": str(t.start_date), "end_date": str(t.end_date)} for t in tts]

@router.post("/upload")
def upload_timetable(file: UploadFile = File(...), user=Depends(require_role("faculty", "admin")),
                    db: Session = Depends(get_db)):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        raise HTTPException(400, "Empty CSV")
    # Minimal: create one timetable from first row's metadata
    # Real impl would parse all rows into entries
    return {"message": f"Received {len(rows)} rows", "columns": list(rows[0].keys())}

@router.get("/today")
def today_timetable(user=Depends(get_current_user), db: Session = Depends(get_db)):
    from datetime import datetime
    today = datetime.utcnow().date()
    day_of_week = today.weekday() - 1  # Monday=0
    entries = db.query(TimetableEntry).join(Timetable).filter(
        Timetable.is_active == True,
        TimetableEntry.day_of_week == day_of_week,
    ).all()
    return [{"period": e.period_number, "start": e.start_time, "end": e.end_time,
             "subject": e.timetable.subject.name, "faculty": e.timetable.faculty.user.first_name + " " + e.timetable.faculty.user.last_name,
             "classroom": e.classroom.room_number if e.classroom else None,
             "floor": e.classroom.floor if e.classroom else None} for e in entries]