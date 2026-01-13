from typing import List
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.student_report_model import StudentReport

class StudentReportRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def create(self, data: dict) -> StudentReport:
        item = StudentReport(**data)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get_all(self) -> List[StudentReport]:
        return self.session.query(StudentReport).all()

    def update_status(self, id: int, status: str, admin_note: str = None):
        item = self.session.query(StudentReport).filter_by(id=id).first()
        if item:
            item.status = status
            if admin_note: item.admin_note = admin_note
            self.session.commit()
            self.session.refresh(item)
        return item