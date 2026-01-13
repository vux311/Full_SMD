from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.faculty_model import Faculty

class FacultyRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[Faculty]:
        return self.session.query(Faculty).all()

    def get_by_id(self, id: int) -> Optional[Faculty]:
        return self.session.query(Faculty).filter_by(id=id).first()

    def create(self, data: dict) -> Faculty:
        faculty = Faculty(**data)
        self.session.add(faculty)
        self.session.commit()
        self.session.refresh(faculty)
        return faculty

    def update(self, id: int, data: dict) -> Optional[Faculty]:
        faculty = self.get_by_id(id)
        if not faculty:
            return None
        for key, value in data.items():
            if hasattr(faculty, key):
                setattr(faculty, key, value)
        self.session.commit()
        self.session.refresh(faculty)
        return faculty

    def delete(self, id: int) -> bool:
        faculty = self.get_by_id(id)
        if not faculty:
            return False
        self.session.delete(faculty)
        self.session.commit()
        return True