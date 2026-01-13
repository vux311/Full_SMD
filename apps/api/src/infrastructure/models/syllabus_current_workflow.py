from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Integer, Date, DateTime, Boolean,
    ForeignKey, UnicodeText, DECIMAL, CheckConstraint, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.databases.base import Base

class SyllabusCurrentWorkflow(Base):
    __tablename__ = 'syllabus_current_workflows'
    
    syllabus_id = Column(BigInteger, ForeignKey('syllabuses.id'), primary_key=True)
    current_state_id = Column(BigInteger, ForeignKey('workflow_states.id'), nullable=False)
    assigned_to_user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    due_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=func.now())
    
    # Relationships
    syllabus = relationship("Syllabus", back_populates="current_workflow")
    current_state = relationship("WorkflowState", back_populates="current_workflows")
    assigned_to_user = relationship("User")
