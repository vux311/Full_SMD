from infrastructure.models.syllabus_snapshot_model import SyllabusSnapshot
from sqlalchemy.orm import Session

class SyllabusSnapshotRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: dict) -> SyllabusSnapshot:
        snapshot = SyllabusSnapshot(**data)
        self.session.add(snapshot)
        self.session.commit()
        return snapshot

    def get_by_syllabus(self, syllabus_id: int):
        return self.session.query(SyllabusSnapshot).filter_by(syllabus_id=syllabus_id).order_by(SyllabusSnapshot.created_at.desc()).all()

    def get_by_id(self, id: int):
        return self.session.query(SyllabusSnapshot).get(id)
