from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from infrastructure.databases.mssql import Base
import datetime

class SyllabusSnapshot(Base):
    __tablename__ = 'syllabus_snapshots'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    syllabus_id = Column(BigInteger, ForeignKey('syllabuses.id'), nullable=False)
    version = Column(String(50), nullable=False)
    snapshot_data = Column(JSON, nullable=False)  # Stores full syllabus details as JSON
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=True)

    syllabus = relationship("Syllabus")
    creator = relationship("User")

    def __repr__(self):
        return f"<SyllabusSnapshot(syllabus_id={self.syllabus_id}, version='{self.version}')>"
