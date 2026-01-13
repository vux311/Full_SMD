from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Integer, Date, DateTime, Boolean,
    ForeignKey, UnicodeText
)
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
# IMPORT BASE CHUNG (QUAN TRỌNG)
from infrastructure.databases.base import Base

class File(Base):
    __tablename__ = 'files'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uploader_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    file_name = Column(NVARCHAR(255), nullable=False)
    file_path = Column(NVARCHAR(500), nullable=False)
    file_size = Column(BigInteger)
    mime_type = Column(NVARCHAR(100))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_files", foreign_keys=[uploader_id])