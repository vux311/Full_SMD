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

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    faculty_id = Column(BigInteger, ForeignKey('faculties.id'), nullable=False)
    code = Column(NVARCHAR(20), unique=True, nullable=False)
    name = Column(NVARCHAR(255), nullable=False)
    
    # Relationships
    faculty = relationship("Faculty", back_populates="departments")
    users = relationship("User", back_populates="department")
    subjects = relationship("Subject", back_populates="department")
    programs = relationship("Program", back_populates="department")
