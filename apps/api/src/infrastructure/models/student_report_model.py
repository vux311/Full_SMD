from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Integer, Date, DateTime, Boolean,
    ForeignKey, UnicodeText, DECIMAL, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.databases.base import Base

class StudentReport(Base):
    __tablename__ = 'student_reports'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    syllabus_id = Column(BigInteger, ForeignKey('syllabuses.id'), nullable=False)
    student_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    content = Column(UnicodeText, nullable=False)
    status = Column(NVARCHAR(20), default='PENDING')  # PENDING, RESOLVED, REJECTED
    admin_note = Column(UnicodeText)
    
    # Relationships
    syllabus = relationship("Syllabus", back_populates="student_reports")
    student = relationship("User")