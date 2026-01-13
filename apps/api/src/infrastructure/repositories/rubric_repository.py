from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.rubric_model import Rubric

class RubricRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[Rubric]:
        return self.session.query(Rubric).filter_by(id=id).first()

    def get_by_component_id(self, component_id: int) -> List[Rubric]:
        return self.session.query(Rubric).filter_by(component_id=component_id).all()

    def create(self, data: dict) -> Rubric:
        item = Rubric(**data)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, id: int, data: dict) -> Optional[Rubric]:
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