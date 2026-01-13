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

class Subject(Base):
    __tablename__ = 'subjects'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    department_id = Column(BigInteger, ForeignKey('departments.id'), nullable=False)
    code = Column(NVARCHAR(20), unique=True, nullable=False)
    name_vi = Column(NVARCHAR(255), nullable=False)
    name_en = Column(NVARCHAR(255), nullable=False)
    credits = Column(Integer, nullable=False)
    credit_theory = Column(DECIMAL(3, 1), default=0)
    credit_practice = Column(DECIMAL(3, 1), default=0)
    credit_self_study = Column(DECIMAL(3, 1), default=0)
    
    # Relationships
    department = relationship("Department", back_populates="subjects")
    syllabuses = relationship("Syllabus", back_populates="subject")
    subject_relationships = relationship("SubjectRelationship", 
                                        foreign_keys="SubjectRelationship.subject_id",
                                        back_populates="subject")
    related_subjects = relationship("SubjectRelationship",
                                   foreign_keys="SubjectRelationship.related_subject_id",
                                   back_populates="related_subject")
    student_subscriptions = relationship("StudentSubscription", back_populates="subject")

