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

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(NVARCHAR(50), unique=True, nullable=False)
    description = Column(NVARCHAR(255), nullable=True)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role")
    workflow_transitions = relationship("WorkflowTransition", back_populates="allowed_role")

