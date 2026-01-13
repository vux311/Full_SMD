from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.academic_year_model import AcademicYear

class AcademicYearRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[AcademicYear]:
        return self.session.query(AcademicYear).all()

    def get_by_id(self, id: int) -> Optional[AcademicYear]:
        return self.session.query(AcademicYear).filter_by(id=id).first()

    def create(self, data: dict) -> AcademicYear:
        ay = AcademicYear(**data)
        self.session.add(ay)
        self.session.commit()
        self.session.refresh(ay)
        return ay

    def update(self, id: int, data: dict) -> Optional[AcademicYear]:
        ay = self.get_by_id(id)
        if not ay:
            return None
        for key, value in data.items():
            if hasattr(ay, key):
                setattr(ay, key, value)
        self.session.commit()
        self.session.refresh(ay)
        return ay

    def delete(self, id: int) -> bool:
        ay = self.get_by_id(id)
        if not ay:
            return False
        self.session.delete(ay)
        self.session.commit()
        return True