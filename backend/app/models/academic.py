import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Date, Text
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Department(Base):
    __tablename__ = "departments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    faculty_profiles = relationship("FacultyProfile", back_populates="department")
    subjects = relationship("Subject", back_populates="department")

class AcademicYear(Base):
    __tablename__ = "academic_years"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)  # e.g. "2026-2027"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

class Semester(Base):
    __tablename__ = "semesters"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False)
    name = Column(String(50), nullable=False)  # "Semester 1"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    academic_year = relationship("AcademicYear")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    credits = Column(Integer, default=3)
    department = relationship("Department", back_populates="subjects")

class Class(Base):
    __tablename__ = "classes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)  # "B.Tech CSE"
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False)
    sections = relationship("Section", back_populates="class_")
    department = relationship("Department")

class Section(Base):
    __tablename__ = "sections"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    name = Column(String(10), nullable=False)  # "A", "B"
    class_ = relationship("Class", back_populates="sections")
    student_profiles = relationship("StudentProfile", back_populates="section")

class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_number = Column(String(20), unique=True, nullable=False)
    floor = Column(Integer, nullable=False)
    building = Column(String(100))
    capacity = Column(Integer, default=60)