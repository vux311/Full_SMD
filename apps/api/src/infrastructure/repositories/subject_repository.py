from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.subject_model import Subject

class SubjectRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[Subject]:
        return self.session.query(Subject).all()

    def get_by_id(self, id: int) -> Optional[Subject]:
        return self.session.query(Subject).filter_by(id=id).first()

    def create(self, data: dict) -> Subject:
        subject = Subject(**data)
        self.session.add(subject)
        self.session.commit()
        self.session.refresh(subject)
        return subject

    def update(self, id: int, data: dict) -> Optional[Subject]:
        subject = self.get_by_id(id)
        if not subject:
            return None
        for key, value in data.items():
            if hasattr(subject, key):
                setattr(subject, key, value)
        self.session.commit()
        self.session.refresh(subject)
        return subject

    def delete(self, id: int) -> bool:
        subject = self.get_by_id(id)
        if not subject:
            return False
        self.session.delete(subject)
        self.session.commit()
        return True