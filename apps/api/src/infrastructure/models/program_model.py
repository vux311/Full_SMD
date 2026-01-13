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

class Program(Base):
    __tablename__ = 'programs'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    department_id = Column(BigInteger, ForeignKey('departments.id'), nullable=False)
    name = Column(NVARCHAR(255), nullable=False)
    total_credits = Column(Integer)
    
    # Relationships
    department = relationship("Department", back_populates="programs")
    outcomes = relationship("ProgramOutcome", back_populates="program")
    syllabuses = relationship("Syllabus", back_populates="program")






    
