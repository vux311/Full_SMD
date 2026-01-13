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

class WorkflowState(Base):
    __tablename__ = 'workflow_states'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(NVARCHAR(50), unique=True, nullable=False)
    name = Column(NVARCHAR(100), nullable=False)
    color = Column(NVARCHAR(20))
    is_final = Column(Boolean, default=False)
    
    # Relationships
    transitions_from = relationship("WorkflowTransition", 
                                   foreign_keys="WorkflowTransition.from_state_id",
                                   back_populates="from_state")
    transitions_to = relationship("WorkflowTransition",
                                 foreign_keys="WorkflowTransition.to_state_id",
                                 back_populates="to_state")
    current_workflows = relationship("SyllabusCurrentWorkflow", back_populates="current_state")
