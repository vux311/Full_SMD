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

class SubjectRelationship(Base):
    __tablename__ = 'subject_relationships'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subject_id = Column(BigInteger, ForeignKey('subjects.id'), nullable=False)
    related_subject_id = Column(BigInteger, ForeignKey('subjects.id'), nullable=False)
    type = Column(NVARCHAR(20), nullable=False)  # PREREQUISITE, COREQUISITE, PARALLEL
    
    # Relationships
    subject = relationship("Subject", foreign_keys=[subject_id], back_populates="subject_relationships")
    related_subject = relationship("Subject", foreign_keys=[related_subject_id], back_populates="related_subjects")
