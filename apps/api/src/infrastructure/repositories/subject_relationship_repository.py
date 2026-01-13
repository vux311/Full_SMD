from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.subject_relationship_model import SubjectRelationship

class SubjectRelationshipRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[SubjectRelationship]:
        return self.session.query(SubjectRelationship).filter_by(id=id).first()

    def get_by_subject(self, subject_id: int) -> List[SubjectRelationship]:
        return self.session.query(SubjectRelationship).filter_by(subject_id=subject_id).all()

    def create(self, data: dict) -> SubjectRelationship:
        item = SubjectRelationship(**data)
        self.session.add(item)
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