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

class SyllabusClo(Base):
    __tablename__ = 'syllabus_clos'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    syllabus_id = Column(BigInteger, ForeignKey('syllabuses.id', ondelete='CASCADE'), nullable=False)
    code = Column(NVARCHAR(20), nullable=False)
    description = Column(UnicodeText, nullable=False)
    embedding_vector = Column(UnicodeText, nullable=True)  # JSON vector
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    syllabus = relationship("Syllabus", back_populates="clos")
    plo_mappings = relationship("CloPloMapping", back_populates="syllabus_clo", cascade="all, delete-orphan")
    assessment_clos = relationship("AssessmentClo", back_populates="syllabus_clo")
