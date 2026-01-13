from typing import List, Optional
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from infrastructure.databases import Base
from infrastructure.databases.mssql import session

# Import the User model
from infrastructure.models.user_model import User

load_dotenv()

class UserRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[User]:
        return self.session.query(User).all()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username with input validation."""
        if not username or not isinstance(username, str):
            return None
        username = username.strip()
        if not username:
            return None
        return self.session.query(User).filter_by(username=username).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()

    def create(self, data: dict) -> User:
        user = User(**data)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update(self, id: int, data: dict) -> Optional[User]:
        user = self.get_by_id(id)
        if not user:
            return None
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, id: int) -> bool:
        user = self.get_by_id(id)
        if not user:
            return False
        self.session.delete(user)
        self.session.commit()
        return True 