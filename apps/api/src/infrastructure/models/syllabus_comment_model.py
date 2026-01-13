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

class SyllabusComment(Base):
    __tablename__ = 'syllabus_comments'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    syllabus_id = Column(BigInteger, ForeignKey('syllabuses.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    content = Column(UnicodeText, nullable=False)
    parent_id = Column(BigInteger, ForeignKey('syllabus_comments.id'), nullable=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    syllabus = relationship("Syllabus", back_populates="comments")
    user = relationship("User", back_populates="comments")
    parent = relationship("SyllabusComment", remote_side=[id], backref="replies")
