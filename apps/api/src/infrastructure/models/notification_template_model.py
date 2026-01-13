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

class NotificationTemplate(Base):
    __tablename__ = 'notification_templates'
    
    code = Column(NVARCHAR(50), primary_key=True)
    title_template = Column(NVARCHAR(255), nullable=False)
    body_template = Column(UnicodeText, nullable=False)
    channel = Column(NVARCHAR(20), default='SYSTEM')  # EMAIL, SMS, SYSTEM

