from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.program_outcome_model import ProgramOutcome

class ProgramOutcomeRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[ProgramOutcome]:
        return self.session.query(ProgramOutcome).filter_by(id=id).first()

    def get_by_program_id(self, program_id: int) -> List[ProgramOutcome]:
        return self.session.query(ProgramOutcome).filter_by(program_id=program_id).all()

    def create(self, data: dict) -> ProgramOutcome:
        item = ProgramOutcome(**data)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, id: int, data: dict) -> Optional[ProgramOutcome]:
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