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

class SyllabusMaterial(Base):
    __tablename__ = 'syllabus_materials'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    syllabus_id = Column(BigInteger, ForeignKey('syllabuses.id', ondelete='CASCADE'), nullable=False)
    type = Column(NVARCHAR(50), nullable=False)  # MAIN, REFERENCE
    title = Column(NVARCHAR(555), nullable=False)
    author = Column(NVARCHAR(255))
    publisher = Column(NVARCHAR(255))
    published_year = Column(Integer)
    isbn = Column(NVARCHAR(50))
    url = Column(UnicodeText, nullable=True)
    
    # Relationships
    syllabus = relationship("Syllabus", back_populates="materials")
