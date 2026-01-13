from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.program_model import Program

class ProgramRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[Program]:
        return self.session.query(Program).all()

    def get_by_id(self, id: int) -> Optional[Program]:
        return self.session.query(Program).filter_by(id=id).first()

    def create(self, data: dict) -> Program:
        p = Program(**data)
        self.session.add(p)
        self.session.commit()
        self.session.refresh(p)
        return p

    def update(self, id: int, data: dict) -> Optional[Program]:
        p = self.get_by_id(id)
        if not p:
            return None
        for key, value in data.items():
            if hasattr(p, key):
                setattr(p, key, value)
        self.session.commit()
        self.session.refresh(p)
        return p

    def delete(self, id: int) -> bool:
        p = self.get_by_id(id)
        if not p:
            return False
        self.session.delete(p)
        self.session.commit()
        return True