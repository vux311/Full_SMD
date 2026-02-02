from typing import List, Optional
from infrastructure.repositories.subject_repository import SubjectRepository
from domain.exceptions import ConflictException

class SubjectService:
    def __init__(self, repository: SubjectRepository):
        self.repository = repository

    def list_subjects(self) -> List:
        return self.repository.get_all()

    def get_subject(self, id: int):
        return self.repository.get_by_id(id)

    def create_subject(self, data: dict):
        if 'code' in data:
            existing = self.repository.get_by_code(data['code'])
            if existing:
                raise ConflictException(f"Subject with code '{data['code']}' already exists.")
        return self.repository.create(data)

    def update_subject(self, id: int, data: dict):
        if 'code' in data:
            existing = self.repository.get_by_code(data['code'])
            if existing and existing.id != id:
                raise ConflictException(f"Subject with code '{data['code']}' already exists.")
        return self.repository.update(id, data)

    def delete_subject(self, id: int) -> bool:
        return self.repository.delete(id)
