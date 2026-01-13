from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.department_model import Department

class DepartmentRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[Department]:
        return self.session.query(Department).all()

    def get_by_id(self, id: int) -> Optional[Department]:
        return self.session.query(Department).filter_by(id=id).first()

    def create(self, data: dict) -> Department:
        department = Department(**data)
        self.session.add(department)
        self.session.commit()
        self.session.refresh(department)
        return department

    def update(self, id: int, data: dict) -> Optional[Department]:
        department = self.get_by_id(id)
        if not department:
            return None
        for key, value in data.items():
            if hasattr(department, key):
                setattr(department, key, value)
        self.session.commit()
        self.session.refresh(department)
        return department

    def delete(self, id: int) -> bool:
        department = self.get_by_id(id)
        if not department:
            return False
        self.session.delete(department)
        self.session.commit()
        return True