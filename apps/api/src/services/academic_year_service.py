from typing import List, Optional
from infrastructure.repositories.academic_year_repository import AcademicYearRepository

class AcademicYearService:
    def __init__(self, repository: AcademicYearRepository):
        self.repository = repository

    def list_academic_years(self) -> List:
        return self.repository.get_all()

    def get_academic_year(self, id: int):
        return self.repository.get_by_id(id)

    def create_academic_year(self, data: dict):
        return self.repository.create(data)

    def update_academic_year(self, id: int, data: dict):
        return self.repository.update(id, data)

    def delete_academic_year(self, id: int) -> bool:
        return self.repository.delete(id)