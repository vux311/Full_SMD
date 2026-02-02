from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Integer, Date, DateTime, Boolean,
    ForeignKey, UnicodeText, DECIMAL, CheckConstraint, UniqueConstraint # <--- Đã thêm UniqueConstraint
)
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.databases.base import Base

class CloPloMapping(Base):
    __tablename__ = 'clo_plo_mappings'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    syllabus_clo_id = Column(BigInteger, ForeignKey('syllabus_clos.id', ondelete='CASCADE'), nullable=False)
    program_plo_id = Column(BigInteger, ForeignKey('program_outcomes.id'), nullable=False)
    level = Column(NVARCHAR(1))  # I, R, M, A
    
    __table_args__ = (
        CheckConstraint("level IN ('I', 'R', 'M', 'A')", name='check_level'),
        # --- FIX: Đảm bảo 1 CLO chỉ map với 1 PLO một lần duy nhất ---
        UniqueConstraint('syllabus_clo_id', 'program_plo_id', name='uq_clo_plo_mapping'),
        # -------------------------------------------------------------
    )
    
    # Relationships
    syllabus_clo = relationship("SyllabusClo", back_populates="plo_mappings")
    program_plo = relationship("ProgramOutcome", back_populates="clo_mappings")