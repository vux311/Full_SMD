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

class StudentSubscription(Base):
    __tablename__ = 'student_subscriptions'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    subject_id = Column(BigInteger, ForeignKey('subjects.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    student = relationship("User")
    subject = relationship("Subject", back_populates="student_subscriptions")