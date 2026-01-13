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

class AssessmentComponent(Base):
    __tablename__ = 'assessment_components'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    scheme_id = Column(BigInteger, ForeignKey('assessment_schemes.id'), nullable=False)
    name = Column(NVARCHAR(255), nullable=False)
    weight = Column(DECIMAL(3, 1), nullable=False)
    
    # Relationships
    scheme = relationship("AssessmentScheme", back_populates="components")
    clos = relationship("AssessmentClo", back_populates="component")
    rubrics = relationship("Rubric", back_populates="component", cascade="all, delete-orphan")
