from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.syllabus_clo_model import SyllabusClo

class SyllabusCloRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[SyllabusClo]:
        return self.session.query(SyllabusClo).all()

    def get_by_id(self, id: int) -> Optional[SyllabusClo]:
        return self.session.query(SyllabusClo).filter_by(id=id).first()

    def get_by_syllabus_id(self, syllabus_id: int) -> List[SyllabusClo]:
        return self.session.query(SyllabusClo).filter_by(syllabus_id=syllabus_id).all()

    def create(self, data: dict) -> SyllabusClo:
        item = SyllabusClo(**data)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, id: int, data: dict) -> Optional[SyllabusClo]:
        item = self.get_by_id(id)
        if not item:
            return None
        for k, v in data.items():
            if hasattr(item, k):
                setattr(item, k, v)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, id: int) -> bool:
        item = self.get_by_id(id)
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True