import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Enum
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class Designation(str, enum.Enum):
    professor = "Professor"
    associate_professor = "Associate Professor"
    assistant_professor = "Assistant Professor"
    lecturer = "Lecturer"

class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    employee_id = Column(String(30), unique=True, nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    designation = Column(String(50), default="Assistant Professor")
    qualification = Column(String(200))
    specialization = Column(String(200))
    is_available = Column(Boolean, default=True)
    user = relationship("User", back_populates="faculty_profile")
    department = relationship("Department", back_populates="faculty_profiles")
    availability = relationship("FacultyAvailability", back_populates="faculty")

class FacultyAvailability(Base):
    __tablename__ = "faculty_availability"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty_profiles.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday ... 6=Sunday
    period_number = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)
    faculty = relationship("FacultyProfile", back_populates="availability")