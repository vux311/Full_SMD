from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from infrastructure.repositories.user_repository import UserRepository
from domain.exceptions import ConflictException

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def list_users(self) -> List:
        return self.repository.get_all()

    def get_user(self, id: int):
        return self.repository.get_by_id(id)

    def get_by_username(self, username: str):
        return self.repository.get_by_username(username)

    def create_user(self, data: dict):
        # Check for duplicates
        if 'username' in data:
            if self.repository.get_by_username(data['username']):
                raise ConflictException(f"Username '{data['username']}' already exists.")
        
        if 'email' in data:
            if self.repository.get_by_email(data['email']):
                raise ConflictException(f"Email '{data['email']}' already exists.")

        # Hash password before saving
        if 'password' in data:
            data['password_hash'] = generate_password_hash(data.pop('password'))
        return self.repository.create(data)

    def update_user(self, id: int, data: dict):
        # Check for duplicates
        if 'username' in data:
            existing = self.repository.get_by_username(data['username'])
            if existing and existing.id != id:
                raise ConflictException(f"Username '{data['username']}' already exists.")
        
        if 'email' in data:
            existing = self.repository.get_by_email(data['email'])
            if existing and existing.id != id:
                raise ConflictException(f"Email '{data['email']}' already exists.")

        if 'password' in data:
            data['password_hash'] = generate_password_hash(data.pop('password'))
        return self.repository.update(id, data)

    def delete_user(self, id: int) -> bool:
        return self.repository.delete(id)

    def authenticate(self, username: str, password: str):
        user = self.get_by_username(username)
        if not user:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        return user