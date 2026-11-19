from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.timetable import Timetable, TimetableEntry
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.substitution import Substitution
from app.models.notification import Notification
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/faculty")
def faculty_dashboard(user=Depends(require_role("faculty")), db: Session = Depends(get_db)):
    from app.models.faculty import FacultyProfile
    fp = db.query(FacultyProfile).filter(FacultyProfile.user_id == user.id).first()
    if not fp:
        return {"error": "No faculty profile"}
    today = datetime.utcnow().date()
    day_of_week = today.weekday() - 1
    today_entries = db.query(TimetableEntry).join(Timetable).filter(
        Timetable.faculty_id == fp.id, Timetable.is_active == True,
        TimetableEntry.day_of_week == day_of_week,
    ).order_by(TimetableEntry.start_time).all()
    today_classes = [{"period": e.period_number, "start": e.start_time, "end": e.end_time,
                      "subject": e.timetable.subject.name, "class": e.timetable.class_.name,
                      "section": e.timetable.section.name,
                      "classroom": e.classroom.room_number if e.classroom else "TBA"} for e in today_entries]
    active_assignments = db.query(Assignment).filter(
        Assignment.faculty_id == fp.id, Assignment.is_cancelled == False).count()
    pending_subs = db.query(Substitution).filter(
        Substitution.substitute_faculty_id == fp.id, Substitution.status == "Pending").count()
    unread = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).count()
    return {
        "faculty_name": f"{user.first_name} {user.last_name}",
        "today_classes": today_classes, "today_count": len(today_classes),
        "active_assignments": active_assignments, "pending_substitutions": pending_subs,
        "unread_notifications": unread,
    }

@router.get("/student")
def student_dashboard(user=Depends(require_role("student")), db: Session = Depends(get_db)):
    from app.models.student import StudentProfile
    sp = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not sp:
        return {"error": "No student profile"}
    today = datetime.utcnow().date()
    day_of_week = today.weekday() - 1
    entries = db.query(TimetableEntry).join(Timetable).filter(
        Timetable.class_id == sp.class_id, Timetable.section_id == sp.section_id,
        Timetable.is_active == True, TimetableEntry.day_of_week == day_of_week,
    ).order_by(TimetableEntry.start_time).all()
    today_classes = [{"period": e.period_number, "start": e.start_time, "end": e.end_time,
                      "subject": e.timetable.subject.name,
                      "faculty": e.timetable.faculty.user.first_name + " " + e.timetable.faculty.user.last_name,
                      "classroom": e.classroom.room_number if e.classroom else "TBA",
                      "floor": e.classroom.floor if e.classroom else "N/A"} for e in entries]
    pending = db.query(Assignment).filter(
        Assignment.class_id == sp.class_id, Assignment.is_cancelled == False).count()
    unread = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).count()
    return {
        "student_name": f"{user.first_name} {user.last_name}",
        "roll_number": sp.roll_number,
        "today_classes": today_classes, "today_count": len(today_classes),
        "pending_assignments": pending, "unread_notifications": unread,
    }

@router.get("/admin")
def admin_dashboard_v2(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    from app.models.user import User as U
    from app.models.faculty import FacultyProfile
    from app.models.student import StudentProfile
    from app.models.timetable import Timetable
    from app.models.assignment import Assignment
    from app.models.substitution import Substitution
    recent = db.query(Notification).order_by(Notification.created_at.desc()).limit(5).all()
    return {
        "total_faculty": db.query(FacultyProfile).count(),
        "total_students": db.query(StudentProfile).count(),
        "total_users": db.query(U).count(),
        "active_timetables": db.query(Timetable).filter(Timetable.is_active == True).count(),
        "total_assignments": db.query(Assignment).filter(Assignment.is_cancelled == False).count(),
        "pending_substitutions": db.query(Substitution).filter(Substitution.status == "Pending").count(),
        "recent_notifications": [{"title": n.title, "created_at": str(n.created_at)} for n in recent],
    }