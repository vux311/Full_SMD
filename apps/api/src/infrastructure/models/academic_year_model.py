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

class AcademicYear(Base):
    __tablename__ = 'academic_years'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(NVARCHAR(20), unique=True)
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Relationships
    syllabuses = relationship("Syllabus", back_populates="academic_year")
