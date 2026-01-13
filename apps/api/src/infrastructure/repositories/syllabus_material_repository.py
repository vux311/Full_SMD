from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.syllabus_material_model import SyllabusMaterial

class SyllabusMaterialRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[SyllabusMaterial]:
        return self.session.query(SyllabusMaterial).all()

    def get_by_id(self, id: int) -> Optional[SyllabusMaterial]:
        return self.session.query(SyllabusMaterial).filter_by(id=id).first()

    def get_by_syllabus_id(self, syllabus_id: int) -> List[SyllabusMaterial]:
        return self.session.query(SyllabusMaterial).filter_by(syllabus_id=syllabus_id).all()

    def create(self, data: dict) -> SyllabusMaterial:
        item = SyllabusMaterial(**data)
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