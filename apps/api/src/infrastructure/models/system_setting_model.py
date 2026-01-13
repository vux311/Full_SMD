from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Integer, Date, DateTime, Boolean,
    ForeignKey, UnicodeText, DECIMAL, CheckConstraint, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.mssql import NVARCHAR
from infrastructure.databases.base import Base

class SystemSetting(Base):
    __tablename__ = 'system_settings'
    
    key = Column(NVARCHAR(50), primary_key=True)
    value = Column(UnicodeText, nullable=False)
    type = Column(NVARCHAR(20), default='STRING')
    description = Column(NVARCHAR(255), nullable=True)