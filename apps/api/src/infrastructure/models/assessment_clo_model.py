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

class AssessmentClo(Base):
    __tablename__ = 'assessment_clos'
    
    assessment_component_id = Column(BigInteger, ForeignKey('assessment_components.id'), primary_key=True)
    syllabus_clo_id = Column(BigInteger, ForeignKey('syllabus_clos.id'), primary_key=True)
    
    # Relationships
    component = relationship("AssessmentComponent", back_populates="clos")
    syllabus_clo = relationship("SyllabusClo", back_populates="assessment_clos")

