from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.role_model import Role

class RoleRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[Role]:
        return self.session.query(Role).all()

    def get_by_id(self, id: int) -> Optional[Role]:
        return self.session.query(Role).filter_by(id=id).first()

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.session.query(Role).filter_by(name=name).first()

    def create(self, data: dict) -> Role:
        role = Role(**data)
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role

    def delete(self, id: int) -> bool:
        role = self.get_by_id(id)
        if not role:
            return False
        self.session.delete(role)
        self.session.commit()
        return True