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

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    department_id = Column(BigInteger, ForeignKey('departments.id'), nullable=True)
    username = Column(NVARCHAR(50), unique=True, nullable=False)
    email = Column(NVARCHAR(100), unique=True, nullable=False)
    password_hash = Column(NVARCHAR(255), nullable=False)
    full_name = Column(NVARCHAR(100), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # SỬA LỖI VÒNG LẶP: Thêm use_alter=True
    avatar_file_id = Column(BigInteger, ForeignKey('files.id', use_alter=True, name='fk_user_avatar_file'), nullable=True)
    
    # Relationships
    department = relationship("Department", back_populates="users")
    
    # Lưu ý: Cập nhật tên relationship nếu file_model dùng tên class là File
    avatar_file = relationship("File", foreign_keys=[avatar_file_id])
    uploaded_files = relationship("File", back_populates="uploader", foreign_keys="File.uploader_id")
    
    roles = relationship("UserRole", back_populates="user")
    syllabuses = relationship("Syllabus", back_populates="lecturer")
    comments = relationship("SyllabusComment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    workflow_logs = relationship("WorkflowLog", back_populates="actor")