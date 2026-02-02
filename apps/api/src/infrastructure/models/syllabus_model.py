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
    
    # Unique constraint to prevent duplicate syllabuses
    __table_args__ = (
        UniqueConstraint('subject_id', 'program_id', 'academic_year_id', 'status', 
                        name='uq_syllabus_active'),
    )
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subject_id = Column(BigInteger, ForeignKey('subjects.id'), nullable=False)
    program_id = Column(BigInteger, ForeignKey('programs.id'), nullable=False)
    academic_year_id = Column(BigInteger, ForeignKey('academic_years.id'), nullable=False)
    lecturer_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    status = Column(String(50), nullable=True, default='DRAFT')
    version = Column(NVARCHAR(10))
    time_allocation = Column(UnicodeText)  # JSON
    prerequisites = Column(UnicodeText)
    
    # Content fields
    description = Column(UnicodeText, nullable=True)  # Mô tả tóm tắt học phần
    objectives = Column(UnicodeText, nullable=True)  # JSON array of course objectives
    student_duties = Column(UnicodeText, nullable=True)  # Nhiệm vụ của sinh viên
    other_requirements = Column(UnicodeText, nullable=True)  # Yêu cầu khác
    
    # Additional metadata
    pre_courses = Column(UnicodeText, nullable=True)  # HP học trước
    co_courses = Column(UnicodeText, nullable=True)  # HP song hành
    course_type = Column(NVARCHAR(50), nullable=True)  # Bắt buộc/Tự chọn
    component_type = Column(NVARCHAR(100), nullable=True)  # Cơ sở ngành, etc.
    date_prepared = Column(NVARCHAR(20), nullable=True)  # Ngày biên soạn
    date_edited = Column(NVARCHAR(20), nullable=True)  # Ngày chỉnh sửa
    dean = Column(NVARCHAR(255), nullable=True)  # Trưởng khoa (Name)
    dean_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    head_department = Column(NVARCHAR(255), nullable=True)  # Trưởng BM (Name)
    head_department_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    
    publish_date = Column(DateTime)
    is_active = Column(Boolean)
    embedding_vector = Column(UnicodeText, nullable=True)  # JSON vector
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    subject = relationship("Subject", back_populates="syllabuses")
    program = relationship("Program", back_populates="syllabuses")
    academic_year = relationship("AcademicYear", back_populates="syllabuses")
    lecturer = relationship("User", back_populates="syllabuses", foreign_keys=[lecturer_id])
    dean_user = relationship("User", foreign_keys=[dean_id])
    head_department_user = relationship("User", foreign_keys=[head_department_id])
    
    clos = relationship("SyllabusClo", back_populates="syllabus", cascade="all, delete-orphan")
    materials = relationship("SyllabusMaterial", back_populates="syllabus", cascade="all, delete-orphan")
    teaching_plans = relationship("TeachingPlan", back_populates="syllabus", cascade="all, delete-orphan")
    assessment_schemes = relationship("AssessmentScheme", back_populates="syllabus", cascade="all, delete-orphan")
    comments = relationship("SyllabusComment", back_populates="syllabus", cascade="all, delete-orphan")
    workflow_logs = relationship("WorkflowLog", back_populates="syllabus", cascade="all, delete-orphan")
    current_workflow = relationship("SyllabusCurrentWorkflow", back_populates="syllabus", uselist=False)
    student_reports = relationship("StudentReport", back_populates="syllabus")
    ai_audit_logs = relationship("AiAuditLog", back_populates="syllabus")
