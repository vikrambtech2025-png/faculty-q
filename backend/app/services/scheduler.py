from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.timetable import Timetable, TimetableEntry
from app.models.student import StudentProfile
from app.services.notification_service import create_class_reminder
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def check_upcoming_classes():
    """Run every minute. Find classes starting in ~5 minutes and send reminders."""
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        target_start = now + timedelta(minutes=4)
        target_time_str = target_start.strftime("%H:%M")
        target_day = target_start.weekday() - 1  # Monday=0

        entries = db.query(TimetableEntry).join(Timetable).filter(
            Timetable.is_active == True,
            TimetableEntry.day_of_week == target_day,
        ).all()

        for entry in entries:
            if entry.start_time == target_time_str:
                faculty_user = entry.timetable.faculty.user
                students = db.query(StudentProfile).filter(
                    StudentProfile.class_id == entry.timetable.class_id,
                    StudentProfile.section_id == entry.timetable.section_id,
                ).all()
                student_users = [s.user for s in students]
                create_class_reminder(db, entry, faculty_user, student_users)
                logger.info("Sent class reminder for period %d - %s", entry.period_number, entry.timetable.subject.name)
    except Exception as e:
        logger.error("Scheduler error: %s", str(e))
    finally:
        db.close()

def check_assignment_deadlines():
    """Run every 15 minutes. Send deadline reminders (24h, 12h, 1h before)."""
    db: Session = SessionLocal()
    try:
        from app.models.assignment import Assignment
        now = datetime.utcnow()
        assignments = db.query(Assignment).filter(Assignment.is_cancelled == False).all()
        for a in assignments:
            for hours_before in [24, 12, 1]:
                reminder_time = a.deadline - timedelta(hours=hours_before)
                # If we're within 5 minutes of the reminder time, send
                if abs((reminder_time - now).total_seconds()) < 300:
                    from app.models.student import StudentProfile
                    students = db.query(StudentProfile).filter(
                        StudentProfile.class_id == a.class_id,
                    ).all()
                    for sp in students:
                        idempotency_key = f"deadline_{a.id}_{sp.id}_{hours_before}h"
                        # Check duplicate
                        from app.models.notification import Notification
                        existing = db.query(Notification).filter(
                            Notification.user_id == sp.user_id,
                            Notification.reference_id == a.id,
                            Notification.notification_type == "assignment_deadline",
                        ).first()
                        if existing:
                            continue
                        title = f"Deadline Reminder: {a.title}"
                        message = (
                            f"Subject: {a.subject.name}\n"
                            f"Faculty: {a.faculty.user.first_name} {a.faculty.user.last_name}\n"
                            f"Deadline: {a.deadline}\n"
                            f"Time remaining: {hours_before} hour(s)\n"
                            f"Status: Pending"
                        )
                        from app.services.notification_service import create_notification
                        create_notification(db, sp.user_id, title, message, "assignment_deadline",
                                            reference_id=a.id, idempotency_key=idempotency_key)
                        logger.info("Sent deadline reminder for %s to %s", a.title, sp.user.email)
    except Exception as e:
        logger.error("Deadline reminder error: %s", str(e))
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(check_upcoming_classes, IntervalTrigger(seconds=60), id="class_reminder", replace_existing=True)
    scheduler.add_job(check_assignment_deadlines, IntervalTrigger(minutes=15), id="deadline_reminder", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started")

def stop_scheduler():
    scheduler.shutdown()