from typing import List, Optional
from infrastructure.repositories.academic_year_repository import AcademicYearRepository
from domain.exceptions import ConflictException

class AcademicYearService:
    def __init__(self, repository: AcademicYearRepository):
        self.repository = repository

    def list_academic_years(self) -> List:
        return self.repository.get_all()

    def get_academic_year(self, id: int):
        return self.repository.get_by_id(id)

    def create_academic_year(self, data: dict):
        if 'code' in data:
            existing = self.repository.get_by_code(data['code'])
            if existing:
                raise ConflictException(f"Academic year with code '{data['code']}' already exists.")
        return self.repository.create(data)

    def update_academic_year(self, id: int, data: dict):
        if 'code' in data:
            existing = self.repository.get_by_code(data['code'])
            if existing and existing.id != id:
                raise ConflictException(f"Academic year with code '{data['code']}' already exists.")
        
        # If activating this academic year, deactivate all others
        if data.get('is_active') or data.get('isActive'):
            all_years = self.repository.get_all()
            for year in all_years:
                if year.id != id and year.is_active:
                    self.repository.update(year.id, {'is_active': False})
            # Ensure the data uses snake_case for database
            data['is_active'] = True
            data.pop('isActive', None)  # Remove camelCase if present
        return self.repository.update(id, data)

    def delete_academic_year(self, id: int) -> bool:
        return self.repository.delete(id)