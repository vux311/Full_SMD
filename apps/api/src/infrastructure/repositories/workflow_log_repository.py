from typing import List
from infrastructure.models.workflow_log_model import WorkflowLog

class WorkflowLogRepository:
    def __init__(self, session):
        self.session = session

    def create(self, data: dict):
        wl = WorkflowLog(**data)
        self.session.add(wl)
        try:
            self.session.commit()
            self.session.refresh(wl)
            return wl
        except Exception:
            self.session.rollback()
            raise

    def get_by_syllabus_id(self, syllabus_id: int) -> List[WorkflowLog]:
        return self.session.query(WorkflowLog).filter_by(syllabus_id=syllabus_id).order_by(WorkflowLog.created_at.asc()).all()