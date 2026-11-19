from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.notification import Notification, NotificationPreference
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/notifications", tags=["notification"])

@router.get("")
def list_notifications(user=Depends(get_current_user), db: Session = Depends(get_db), unread_only: bool = False):
    q = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    notifs = q.order_by(Notification.created_at.desc()).limit(50).all()
    return [{"id": str(n.id), "title": n.title, "message": n.message,
             "type": n.notification_type, "is_read": n.is_read,
             "created_at": str(n.created_at)} for n in notifs]

@router.get("/unread-count")
def unread_count(user=Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).count()
    return {"count": count}

@router.put("/{nid}/read")
def mark_read(nid: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == nid, Notification.user_id == user.id).first()
    if not n:
        raise HTTPException(404, "Not found")
    n.is_read = True
    db.commit()
    return {"id": str(n.id), "is_read": True}

@router.put("/read-all")
def mark_all_read(user=Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"message": "All marked as read"}

@router.get("/preferences")
def get_prefs(user=Depends(get_current_user), db: Session = Depends(get_db)):
    pref = db.query(NotificationPreference).filter(NotificationPreference.user_id == user.id).first()
    if not pref:
        pref = NotificationPreference(user_id=user.id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return {"email_enabled": pref.email_enabled, "in_app_enabled": pref.in_app_enabled,
            "class_reminder_minutes": pref.class_reminder_minutes}

@router.post("/test-email")
def test_email(user=Depends(get_current_user)):
    from app.services.email_service import send_email
    from app.core.config import settings
    if not settings.SMTP_HOST:
        return {"status": "not_configured", "message": "SMTP not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD env vars."}
    success = send_email(user.email, "FACULTY Q - Test Email", "This is a test email from FACULTY Q. If you received this, email is configured correctly.")
    return {"status": "sent" if success else "failed", "message": "Test email sent" if success else "Failed to send. Check SMTP credentials and logs."}

@router.put("/preferences")
def update_prefs(email_enabled: bool = None, in_app_enabled: bool = None,
                 user=Depends(get_current_user), db: Session = Depends(get_db)):
    pref = db.query(NotificationPreference).filter(NotificationPreference.user_id == user.id).first()
    if not pref:
        pref = NotificationPreference(user_id=user.id)
        db.add(pref)
    if email_enabled is not None:
        pref.email_enabled = email_enabled
    if in_app_enabled is not None:
        pref.in_app_enabled = in_app_enabled
    db.commit()
    return {"message": "Preferences updated"}