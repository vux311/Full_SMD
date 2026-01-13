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

class AssessmentScheme(Base):
    __tablename__ = 'assessment_schemes'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    syllabus_id = Column(BigInteger, ForeignKey('syllabuses.id', ondelete='CASCADE'), nullable=False)
    name = Column(NVARCHAR(100))
    weight = Column(DECIMAL(3, 1))
    
    # Relationships
    syllabus = relationship("Syllabus", back_populates="assessment_schemes")
    components = relationship("AssessmentComponent", back_populates="scheme", cascade="all, delete-orphan")
