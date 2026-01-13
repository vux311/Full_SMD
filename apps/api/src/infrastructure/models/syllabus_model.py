from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Integer, Date, DateTime, Boolean,
    ForeignKey, UnicodeText, DECIMAL, CheckConstraint, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.mssql import NVARCHAR
from infrastructure.databases.base import Base

class Syllabus(Base):
    __tablename__ = 'syllabuses'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subject_id = Column(BigInteger, ForeignKey('subjects.id'), nullable=False)
    program_id = Column(BigInteger, ForeignKey('programs.id'), nullable=False)
    academic_year_id = Column(BigInteger, ForeignKey('academic_years.id'), nullable=False)
    lecturer_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    status = Column(NVARCHAR(20))  # DRAFT, PENDING, APPROVED
    version = Column(NVARCHAR(10))
    time_allocation = Column(UnicodeText)  # JSON
    prerequisites = Column(UnicodeText)
    publish_date = Column(DateTime)
    is_active = Column(Boolean)
    embedding_vector = Column(UnicodeText, nullable=True)  # JSON vector
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    subject = relationship("Subject", back_populates="syllabuses")
    program = relationship("Program", back_populates="syllabuses")
    academic_year = relationship("AcademicYear", back_populates="syllabuses")
    lecturer = relationship("User", back_populates="syllabuses")
    clos = relationship("SyllabusClo", back_populates="syllabus", cascade="all, delete-orphan")
    materials = relationship("SyllabusMaterial", back_populates="syllabus", cascade="all, delete-orphan")
    teaching_plans = relationship("TeachingPlan", back_populates="syllabus", cascade="all, delete-orphan")
    assessment_schemes = relationship("AssessmentScheme", back_populates="syllabus", cascade="all, delete-orphan")
    comments = relationship("SyllabusComment", back_populates="syllabus")
    workflow_logs = relationship("WorkflowLog", back_populates="syllabus")
    current_workflow = relationship("SyllabusCurrentWorkflow", back_populates="syllabus", uselist=False)
    student_reports = relationship("StudentReport", back_populates="syllabus")
    ai_audit_logs = relationship("AiAuditLog", back_populates="syllabus")
