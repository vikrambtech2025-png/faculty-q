import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # class_reminder, assignment_deadline, substitution, system
    reference_id = Column(UUID(as_uuid=True))  # ID of related entity
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    email_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    class_reminder_minutes = Column(Integer, default=5)
    deadline_reminder_hours = Column(String(50), default="24,12,1")
    user = relationship("User")

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id"), nullable=False)
    channel = Column(String(20), nullable=False)  # in_app, email
    status = Column(String(20), default="pending")  # pending, sent, failed, retrying
    error_message = Column(Text)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    notification = relationship("Notification")

class EmailDeliveryLog(Base):
    __tablename__ = "email_delivery_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(200), nullable=False)
    status = Column(String(20), default="pending")
    error_message = Column(Text)
    sent_at = Column(DateTime)
    idempotency_key = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)