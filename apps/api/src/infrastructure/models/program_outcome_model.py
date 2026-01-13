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

class ProgramOutcome(Base):
    __tablename__ = 'program_outcomes'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    program_id = Column(BigInteger, ForeignKey('programs.id'), nullable=False)
    code = Column(NVARCHAR(20))
    description = Column(UnicodeText)
    
    # Relationships
    program = relationship("Program", back_populates="outcomes")
    clo_mappings = relationship("CloPloMapping", back_populates="program_plo")