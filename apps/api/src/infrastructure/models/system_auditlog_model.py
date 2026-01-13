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

class SystemAuditLog(Base):
    __tablename__ = 'system_audit_logs'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    action_type = Column(NVARCHAR(50), nullable=False)
    resource_target = Column(NVARCHAR(100))
    ip_address = Column(NVARCHAR(45))
    user_agent = Column(UnicodeText)
    details = Column(UnicodeText)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User")

