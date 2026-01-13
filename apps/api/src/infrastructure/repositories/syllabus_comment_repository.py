from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.syllabus_comment_model import SyllabusComment

class SyllabusCommentRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[SyllabusComment]:
        return self.session.query(SyllabusComment).filter_by(id=id).first()

    def get_by_syllabus(self, syllabus_id: int) -> List[SyllabusComment]:
        return self.session.query(SyllabusComment).filter_by(syllabus_id=syllabus_id).order_by(SyllabusComment.created_at.asc()).all()

    def create(self, data: dict) -> SyllabusComment:
        item = SyllabusComment(**data)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, id: int, data: dict) -> Optional[SyllabusComment]:
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