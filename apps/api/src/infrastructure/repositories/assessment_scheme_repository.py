from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from infrastructure.databases.mssql import session
from infrastructure.models.assessment_scheme_model import AssessmentScheme

class AssessmentSchemeRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[AssessmentScheme]:
        return self.session.query(AssessmentScheme).all()

    def get_by_id(self, id: int) -> Optional[AssessmentScheme]:
        return self.session.query(AssessmentScheme).filter_by(id=id).first()

    def get_by_syllabus_id(self, syllabus_id: int) -> List[AssessmentScheme]:
        # Load components eagerly
        return self.session.query(AssessmentScheme).options(joinedload(AssessmentScheme.components)).filter_by(syllabus_id=syllabus_id).all()

    def create(self, data: dict) -> AssessmentScheme:
        s = AssessmentScheme(**data)
        self.session.add(s)
        self.session.commit()
        self.session.refresh(s)
        return s

    def update(self, id: int, data: dict) -> Optional[AssessmentScheme]:
        s = self.get_by_id(id)
        if not s:
            return None
        for k, v in data.items():
            if hasattr(s, k):
                setattr(s, k, v)
        self.session.commit()
        self.session.refresh(s)
        return s

    def delete(self, id: int) -> bool:
        s = self.get_by_id(id)
        if not s:
            return False
        self.session.delete(s)
        self.session.commit()
        return True