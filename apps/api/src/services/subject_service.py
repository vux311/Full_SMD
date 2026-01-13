from typing import List, Optional
from infrastructure.repositories.subject_repository import SubjectRepository

class SubjectService:
    def __init__(self, repository: SubjectRepository):
        self.repository = repository

    def list_subjects(self) -> List:
        return self.repository.get_all()

    def get_subject(self, id: int):
        return self.repository.get_by_id(id)

    def create_subject(self, data: dict):
        return self.repository.create(data)

    def update_subject(self, id: int, data: dict):
        return self.repository.update(id, data)

    def delete_subject(self, id: int) -> bool:
        return self.repository.delete(id)
