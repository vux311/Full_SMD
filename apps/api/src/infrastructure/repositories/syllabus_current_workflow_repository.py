from typing import Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.syllabus_current_workflow import SyllabusCurrentWorkflow

class SyllabusCurrentWorkflowRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_by_syllabus_id(self, syllabus_id: int) -> Optional[SyllabusCurrentWorkflow]:
        return self.session.query(SyllabusCurrentWorkflow).filter_by(syllabus_id=syllabus_id).first()

    def update_or_create(self, syllabus_id: int, data: dict) -> SyllabusCurrentWorkflow:
        cw = self.get_by_syllabus_id(syllabus_id)
        if cw:
            for key, value in data.items():
                if hasattr(cw, key):
                    setattr(cw, key, value)
        else:
            cw = SyllabusCurrentWorkflow(syllabus_id=syllabus_id, **data)
            self.session.add(cw)
        
        self.session.commit()
        self.session.refresh(cw)
        return cw

    def delete(self, syllabus_id: int) -> bool:
        cw = self.get_by_syllabus_id(syllabus_id)
        if not cw:
            return False
        self.session.delete(cw)
        self.session.commit()
        return True

    def get_overdue(self):
        from datetime import datetime
        return self.session.query(SyllabusCurrentWorkflow).filter(
            SyllabusCurrentWorkflow.due_date < datetime.now()
        ).all()
