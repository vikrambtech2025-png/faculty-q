import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationPreference, NotificationLog, EmailDeliveryLog
from app.services.email_service import send_email
import logging

logger = logging.getLogger(__name__)

def create_notification(db: Session, user_id, title: str, message: str,
                       ntype: str, reference_id=None, idempotency_key: str = None) -> Notification:
    """Create an in-app notification. Prevents duplicates via idempotency_key on email logs."""
    from uuid import UUID as PyUUID
    uid = PyUUID(str(user_id)) if not isinstance(user_id, PyUUID) else user_id
    rid = PyUUID(str(reference_id)) if reference_id and not isinstance(reference_id, PyUUID) else reference_id
    # Check for duplicate in-app notification
    if rid:
        existing = db.query(Notification).filter(
            Notification.user_id == uid,
            Notification.reference_id == rid,
            Notification.notification_type == ntype,
        ).first()
        if existing:
            return existing
    user_id = uid
    reference_id = rid

    notif = Notification(
        user_id=user_id, title=title, message=message,
        notification_type=ntype, reference_id=reference_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    # Send email if user has email notifications enabled
    _send_email_notification(db, notif, idempotency_key)
    return notif

def _send_email_notification(db: Session, notif: Notification, idempotency_key: str = None):
    user = notif.user
    pref = db.query(NotificationPreference).filter(NotificationPreference.user_id == user.id).first()
    if not pref or not pref.email_enabled:
        return

    # Check idempotency
    if idempotency_key:
        existing_log = db.query(EmailDeliveryLog).filter(
            EmailDeliveryLog.idempotency_key == idempotency_key
        ).first()
        if existing_log:
            return  # Already sent

    log = EmailDeliveryLog(
        recipient_email=user.email,
        subject=notif.title,
        status="pending",
        idempotency_key=idempotency_key,
    )
    db.add(log)
    db.commit()

    success = send_email(user.email, notif.title, notif.message)
    log.status = "sent" if success else "failed"
    log.sent_at = datetime.utcnow() if success else None
    if not success:
        log.error_message = "SMTP delivery failed"
    db.commit()

    # Also create notification log
    nlog = NotificationLog(
        notification_id=notif.id,
        channel="email",
        status="sent" if success else "failed",
        sent_at=datetime.utcnow() if success else None,
    )
    db.add(nlog)
    db.commit()

def create_class_reminder(db: Session, timetable_entry, faculty_user, student_users: list):
    """Create 5-min-before-class reminders for faculty and students."""
    subject_name = timetable_entry.timetable.subject.name
    class_name = timetable_entry.timetable.class_.name
    section = timetable_entry.timetable.section.name
    classroom = timetable_entry.classroom.room_number if timetable_entry.classroom else "TBA"
    floor = timetable_entry.classroom.floor if timetable_entry.classroom else "N/A"
    period = timetable_entry.period_number
    faculty_name = timetable_entry.timetable.faculty.user.first_name + " " + timetable_entry.timetable.faculty.user.last_name
    start_time = timetable_entry.start_time

    title = f"Class Reminder: {subject_name}"
    message = (
        f"Faculty: {faculty_name}\n"
        f"Subject: {subject_name}\n"
        f"Period: {period}\n"
        f"Class: {class_name} - Section {section}\n"
        f"Classroom: {classroom}, Floor: {floor}\n"
        f"Time: {start_time}\n"
        f"Your class starts in 5 minutes."
    )

    # Notify faculty
    idempotency_key = f"class_reminder_faculty_{timetable_entry.id}_{timetable_entry.timetable.start_date}"
    create_notification(db, faculty_user.id, title, message, "class_reminder",
                        reference_id=timetable_entry.id, idempotency_key=idempotency_key)

    # Notify students
    for student in student_users:
        key = f"class_reminder_student_{student.id}_{timetable_entry.id}_{timetable_entry.timetable.start_date}"
        create_notification(db, student.id, title, message, "class_reminder",
                            reference_id=timetable_entry.id, idempotency_key=key)