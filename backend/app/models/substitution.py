import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Enum
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class SubstitutionStatus(str, enum.Enum):
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"
    completed = "Completed"

class Substitution(Base):
    __tablename__ = "substitutions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timetable_entry_id = Column(UUID(as_uuid=True), ForeignKey("timetable_entries.id"), nullable=False)
    original_faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty_profiles.id"), nullable=False)
    substitute_faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty_profiles.id"), nullable=False)
    substitution_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="Pending")
    reason = Column(Text)
    notes = Column(Text)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    timetable_entry = relationship("TimetableEntry")
    original_faculty = relationship("FacultyProfile", foreign_keys=[original_faculty_id])
    substitute_faculty = relationship("FacultyProfile", foreign_keys=[substitute_faculty_id])