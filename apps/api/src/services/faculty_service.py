from typing import List, Optional
from infrastructure.repositories.faculty_repository import FacultyRepository

class FacultyService:
    def __init__(self, repository: FacultyRepository):
        self.repository = repository

    def list_faculties(self) -> List:
        return self.repository.get_all()

    def get_faculty(self, id: int):
        return self.repository.get_by_id(id)

    def create_faculty(self, data: dict):
        return self.repository.create(data)

    def update_faculty(self, id: int, data: dict):
        return self.repository.update(id, data)

    def delete_faculty(self, id: int) -> bool:
        return self.repository.delete(id)