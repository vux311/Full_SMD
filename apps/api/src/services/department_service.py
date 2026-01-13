from typing import List, Optional
from infrastructure.repositories.department_repository import DepartmentRepository

class DepartmentService:
    def __init__(self, repository: DepartmentRepository):
        self.repository = repository

    def list_departments(self) -> List:
        return self.repository.get_all()

    def get_department(self, id: int):
        return self.repository.get_by_id(id)

    def create_department(self, data: dict):
        return self.repository.create(data)

    def update_department(self, id: int, data: dict):
        return self.repository.update(id, data)

    def delete_department(self, id: int) -> bool:
        return self.repository.delete(id)