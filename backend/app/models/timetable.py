import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Date
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class TimetableVersion(Base):
    __tablename__ = "timetable_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_number = Column(Integer, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Timetable(Base):
    __tablename__ = "timetables"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty_profiles.id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    semester_id = Column(UUID(as_uuid=True), ForeignKey("semesters.id"), nullable=False)
    version_id = Column(UUID(as_uuid=True), ForeignKey("timetable_versions.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    faculty = relationship("FacultyProfile")
    class_ = relationship("Class")
    section = relationship("Section")
    subject = relationship("Subject")
    entries = relationship("TimetableEntry", back_populates="timetable", cascade="all, delete-orphan")

class TimetableEntry(Base):
    __tablename__ = "timetable_entries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timetable_id = Column(UUID(as_uuid=True), ForeignKey("timetables.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday
    period_number = Column(Integer, nullable=False)
    start_time = Column(String(5), nullable=False)  # "09:00"
    end_time = Column(String(5), nullable=False)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"))
    timetable = relationship("Timetable", back_populates="entries")
    classroom = relationship("Classroom")