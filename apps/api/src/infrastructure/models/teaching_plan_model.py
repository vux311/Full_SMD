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

class TeachingPlan(Base):
    __tablename__ = 'teaching_plans'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    syllabus_id = Column(BigInteger, ForeignKey('syllabuses.id', ondelete='CASCADE'), nullable=False)
    week = Column(Integer)
    topic = Column(UnicodeText)
    activity = Column(UnicodeText)
    assessment = Column(UnicodeText)
    
    # Relationships
    syllabus = relationship("Syllabus", back_populates="teaching_plans")