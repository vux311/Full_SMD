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

class WorkflowTransition(Base):
    __tablename__ = 'workflow_transitions'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    from_state_id = Column(BigInteger, ForeignKey('workflow_states.id'), nullable=False)
    to_state_id = Column(BigInteger, ForeignKey('workflow_states.id'), nullable=False)
    allowed_role_id = Column(BigInteger, ForeignKey('roles.id'), nullable=False)
    action_name = Column(NVARCHAR(50))
    
    # Relationships
    from_state = relationship("WorkflowState", foreign_keys=[from_state_id], back_populates="transitions_from")
    to_state = relationship("WorkflowState", foreign_keys=[to_state_id], back_populates="transitions_to")
    allowed_role = relationship("Role", back_populates="workflow_transitions")

