from sqlalchemy import Column, Integer, String, DateTime, Boolean
from infrastructure.databases.base import Base

class User:
    
    def __innit__(self, user_name: str, password: str, description: str = None, status: bool = True):
        self.user_name = user_name
        self.password = password
        self.description = description
        self.status = status
        self.created_at = None
        self.updated_at = None