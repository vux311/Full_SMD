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

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        if not email or not isinstance(email, str):
            return None
        return self.session.query(User).filter_by(email=email).first()

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
        
        # Delete related user_roles entries first (junction table)
        from infrastructure.models.user_role_model import UserRole
        self.session.query(UserRole).filter(UserRole.user_id == id).delete()
        
        # Now delete the user
        self.session.delete(user)
        self.session.commit()
        return True 
    def get_users_by_role(self, role_name: str) -> List[User]:
        from infrastructure.models.user_role_model import UserRole
        from infrastructure.models.role_model import Role
        return (self.session.query(User)
                .join(UserRole, User.id == UserRole.user_id)
                .join(Role, UserRole.role_id == Role.id)
                .filter(Role.name == role_name)
                .all())
