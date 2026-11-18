from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.timetable import Timetable, TimetableEntry, TimetableVersion
from app.models.academic import Subject, Class, Section, Classroom, Semester
from app.models.faculty import FacultyProfile
from app.models.student import StudentProfile
from datetime import date, timedelta, datetime
import csv, io, uuid

router = APIRouter(prefix="/api/timetables", tags=["timetable"])

DAY_MAP = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}

@router.get("")
def list_timetables(user=Depends(get_current_user), db: Session = Depends(get_db),
                    faculty_id: str = None, class_id: str = None, section_id: str = None):
    q = db.query(Timetable).filter(Timetable.is_active == True)
    from uuid import UUID as PyUUID
    if faculty_id:
        q = q.filter(Timetable.faculty_id == PyUUID(faculty_id))
    if class_id:
        q = q.filter(Timetable.class_id == PyUUID(class_id))
    if section_id:
        q = q.filter(Timetable.section_id == PyUUID(section_id))
    tts = q.all()
    return [{"id": str(t.id), "faculty": t.faculty.user.first_name + " " + t.faculty.user.last_name,
             "faculty_id": str(t.faculty_id), "subject": t.subject.name, "subject_id": str(t.subject_id),
             "class": t.class_.name, "class_id": str(t.class_id), "section": t.section.name,
             "section_id": str(t.section_id), "start_date": str(t.start_date), "end_date": str(t.end_date),
             "is_approved": t.is_approved, "version": t.version_id and str(t.version_id)} for t in tts]

@router.get("/history")
def timetable_history(user=Depends(get_current_user), db: Session = Depends(get_db)):
    tts = db.query(Timetable).order_by(Timetable.created_at.desc()).all()
    return [{"id": str(t.id), "faculty": t.faculty.user.first_name + " " + t.faculty.user.last_name,
             "subject": t.subject.name, "class": t.class_.name, "section": t.section.name,
             "start_date": str(t.start_date), "end_date": str(t.end_date),
             "is_active": t.is_active, "is_approved": t.is_approved} for t in tts]

@router.get("/today")
def today_timetable(user=Depends(get_current_user), db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    day_of_week = today.weekday() - 1
    entries = db.query(TimetableEntry).join(Timetable).filter(
        Timetable.is_active == True,
        TimetableEntry.day_of_week == day_of_week,
    ).all()
    return [{"period": e.period_number, "start": e.start_time, "end": e.end_time,
             "subject": e.timetable.subject.name, "faculty": e.timetable.faculty.user.first_name + " " + e.timetable.faculty.user.last_name,
             "class": e.timetable.class_.name, "section": e.timetable.section.name,
             "classroom": e.classroom.room_number if e.classroom else None,
             "floor": e.classroom.floor if e.classroom else None} for e in entries]

@router.get("/week")
def week_timetable(user=Depends(get_current_user), db: Session = Depends(get_db)):
    entries = db.query(TimetableEntry).join(Timetable).filter(Timetable.is_active == True).all()
    result = {}
    for e in entries:
        day = e.day_of_week
        result.setdefault(day, []).append({
            "period": e.period_number, "start": e.start_time, "end": e.end_time,
            "subject": e.timetable.subject.name, "faculty": e.timetable.faculty.user.first_name + " " + e.timetable.faculty.user.last_name,
            "class": e.timetable.class_.name, "section": e.timetable.section.name,
            "classroom": e.classroom.room_number if e.classroom else None,
        })
    return result

@router.post("/upload")
def upload_timetable(file: UploadFile = File(...), user=Depends(get_current_user),
                    db: Session = Depends(get_db)):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        raise HTTPException(400, "Empty CSV")
    # Expected columns: faculty_email, subject_code, class_name, section_name, day, period, start_time, end_time, classroom, semester
    required = {"faculty_email", "subject_code", "class_name", "section_name", "day", "period", "start_time", "end_time"}
    missing = required - set(rows[0].keys())
    if missing:
        raise HTTPException(400, f"Missing columns: {missing}")

    # Group rows by (faculty, subject, class, section, semester) to create timetables
    groups = {}
    for row in rows:
        key = (row["faculty_email"], row["subject_code"], row["class_name"], row["section_name"], row.get("semester", "Semester 1"))
        groups.setdefault(key, []).append(row)

    conflicts = []
    created_timetables = []

    for key, group_rows in groups.items():
        faculty_email, subject_code, class_name, section_name, sem_name = key
        faculty_user = db.query(User := __import__("app.models.user", fromlist=["User"]).User).filter(User.email == faculty_email).first() if False else None
        from app.models.user import User as U
        fu = db.query(U).filter(U.email == faculty_email).first()
        if not fu or not fu.faculty_profile:
            conflicts.append(f"Faculty not found: {faculty_email}")
            continue
        fp = fu.faculty_profile
        subject = db.query(Subject).filter(Subject.code == subject_code).first()
        if not subject:
            conflicts.append(f"Subject not found: {subject_code}")
            continue
        cls = db.query(Class).filter(Class.name == class_name).first()
        if not cls:
            conflicts.append(f"Class not found: {class_name}")
            continue
        sec = db.query(Section).filter(Section.class_id == cls.id, Section.name == section_name).first()
        if not sec:
            conflicts.append(f"Section not found: {section_name} in {class_name}")
            continue
        sem = db.query(Semester).filter(Semester.name == sem_name).first()
        if not sem:
            sem = db.query(Semester).first()

        # Conflict detection: check faculty not double-booked
        for row in group_rows:
            day = DAY_MAP.get(row["day"].lower().strip())
            if day is None:
                conflicts.append(f"Invalid day: {row['day']}")
                continue
            period = int(row["period"])
            existing = db.query(TimetableEntry).join(Timetable).filter(
                Timetable.faculty_id == fp.id,
                Timetable.is_active == True,
                TimetableEntry.day_of_week == day,
                TimetableEntry.period_number == period,
            ).first()
            if existing:
                conflicts.append(f"Faculty {faculty_email} already has a class on {row['day']} period {period}")
            # Classroom conflict
            room_no = row.get("classroom", "").strip()
            if room_no:
                room = db.query(Classroom).filter(Classroom.room_number == room_no).first()
                if room:
                    room_conflict = db.query(TimetableEntry).join(Timetable).filter(
                        TimetableEntry.classroom_id == room.id,
                        TimetableEntry.day_of_week == day,
                        TimetableEntry.period_number == period,
                        Timetable.is_active == True,
                    ).first()
                    if room_conflict:
                        conflicts.append(f"Classroom {room_no} already booked on {row['day']} period {period}")

        if conflicts and any(c.startswith("Faculty") or c.startswith("Classroom") for c in conflicts):
            continue

        # Create version
        version = db.query(TimetableVersion).order_by(TimetableVersion.version_number.desc()).first()
        new_ver_num = (version.version_number + 1) if version else 1
        ver = TimetableVersion(version_number=new_ver_num, description=f"Upload by {user.email}")
        db.add(ver)
        db.flush()

        # Deactivate old timetables for this faculty+class+section
        old_tts = db.query(Timetable).filter(
            Timetable.faculty_id == fp.id,
            Timetable.class_id == cls.id,
            Timetable.section_id == sec.id,
            Timetable.is_active == True,
        ).all()
        for ot in old_tts:
            ot.is_active = False

        # Create new timetable
        tt = Timetable(
            faculty_id=fp.id, class_id=cls.id, section_id=sec.id,
            subject_id=subject.id, semester_id=sem.id, version_id=ver.id,
            start_date=date.today(), end_date=date.today() + timedelta(days=180),
            is_active=True, is_approved=False,
        )
        db.add(tt)
        db.flush()

        # Create entries
        for row in group_rows:
            day = DAY_MAP[row["day"].lower().strip()]
            period = int(row["period"])
            room_no = row.get("classroom", "").strip()
            room = db.query(Classroom).filter(Classroom.room_number == room_no).first() if room_no else None
            entry = TimetableEntry(
                timetable_id=tt.id, day_of_week=day, period_number=period,
                start_time=row["start_time"].strip(), end_time=row["end_time"].strip(),
                classroom_id=room.id if room else None,
            )
            db.add(entry)

        created_timetables.append(str(tt.id))

    db.commit()

    return {
        "message": f"Processed {len(rows)} rows",
        "timetables_created": len(created_timetables),
        "conflicts": conflicts,
        "ids": created_timetables,
    }

@router.put("/{tid}/approve")
def approve_timetable(tid: str, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    from uuid import UUID as PyUUID
    tt = db.query(Timetable).filter(Timetable.id == PyUUID(tid)).first()
    if not tt:
        raise HTTPException(404, "Not found")
    tt.is_approved = True
    db.commit()
    return {"id": str(tt.id), "is_approved": True}

@router.put("/{tid}/deactivate")
def deactivate(tid: str, user=Depends(require_role("admin", "faculty")), db: Session = Depends(get_db)):
    from uuid import UUID as PyUUID
    tt = db.query(Timetable).filter(Timetable.id == PyUUID(tid)).first()
    if not tt:
        raise HTTPException(404, "Not found")
    tt.is_active = False
    db.commit()
    return {"id": str(tt.id), "is_active": False}