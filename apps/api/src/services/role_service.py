from typing import List, Optional
from infrastructure.repositories.role_repository import RoleRepository

class RoleService:
    def __init__(self, repository: RoleRepository):
        self.repository = repository

    def list_roles(self) -> List:
        return self.repository.get_all()

    def get_role(self, id: int):
        return self.repository.get_by_id(id)

    def get_by_name(self, name: str):
        return self.repository.get_by_name(name)

    def create_role(self, data: dict):
        return self.repository.create(data)

    def delete_role(self, id: int) -> bool:
        return self.repository.delete(id)