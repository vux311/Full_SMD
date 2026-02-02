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
    state = Column(NVARCHAR(50), nullable=False)  # Current string state (DRAFT, PENDING, etc.)
    current_state_id = Column(BigInteger, ForeignKey('workflow_states.id'), nullable=True)
    assigned_user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    assigned_to_user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True) # Legacy
    due_date = Column(DateTime, nullable=True)
    last_action_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now()) # Legacy
    
    # Relationships
    syllabus = relationship("Syllabus", back_populates="current_workflow")
    current_state = relationship("WorkflowState", back_populates="current_workflows")
    assigned_to_user = relationship("User", foreign_keys=[assigned_user_id])
    assigned_to_user_legacy = relationship("User", foreign_keys=[assigned_to_user_id])
