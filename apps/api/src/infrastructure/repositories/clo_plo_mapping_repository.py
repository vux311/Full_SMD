from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.clo_plo_mapping_model import CloPloMapping

class CloPloMappingRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[CloPloMapping]:
        return self.session.query(CloPloMapping).filter_by(id=id).first()

    def get_by_syllabus_clo(self, syllabus_clo_id: int) -> List[CloPloMapping]:
        return self.session.query(CloPloMapping).filter_by(syllabus_clo_id=syllabus_clo_id).all()

    def create(self, data: dict) -> CloPloMapping:
        item = CloPloMapping(**data)
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