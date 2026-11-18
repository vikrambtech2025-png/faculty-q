import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"))
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty_profiles.id"), nullable=False)
    deadline = Column(DateTime, nullable=False)
    attachments = Column(Text)  # JSON list of file paths
    is_cancelled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    subject = relationship("Subject")
    class_ = relationship("Class")
    faculty = relationship("FacultyProfile")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty_profiles.id"), nullable=False)
    deadline = Column(DateTime, nullable=False)
    attachments = Column(Text)
    is_cancelled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    subject = relationship("Subject")
    class_ = relationship("Class")
    faculty = relationship("FacultyProfile")

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False)
    submitted_at = Column(DateTime)
    file_path = Column(String(500))
    status = Column(String(20), default="Pending")  # Pending, Submitted, Overdue, Completed
    grade = Column(String(10))
    feedback = Column(Text)
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("StudentProfile")