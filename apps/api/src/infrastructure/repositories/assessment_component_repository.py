from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.assessment_component_model import AssessmentComponent

class AssessmentComponentRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[AssessmentComponent]:
        return self.session.query(AssessmentComponent).filter_by(id=id).first()

    def create(self, data: dict) -> AssessmentComponent:
        item = AssessmentComponent(**data)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, id: int, data: dict) -> Optional[AssessmentComponent]:
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