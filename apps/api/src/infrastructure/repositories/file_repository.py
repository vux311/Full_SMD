from typing import Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.file_model import File

class FileRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[File]:
        return self.session.query(File).filter_by(id=id).first()

    def create(self, data: dict) -> File:
        file_record = File(**data)
        self.session.add(file_record)
        self.session.commit()
        self.session.refresh(file_record)
        return file_record

    def delete(self, id: int) -> bool:
        item = self.get_by_id(id)
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True