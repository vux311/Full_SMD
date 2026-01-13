from typing import List, Optional
from infrastructure.repositories.syllabus_clo_repository import SyllabusCloRepository

class SyllabusCloService:
    def __init__(self, repository: SyllabusCloRepository, syllabus_repository=None):
        self.repository = repository
        self.syllabus_repository = syllabus_repository

    def list_clos(self) -> List:
        return self.repository.get_all()

    def get_clo(self, id: int):
        return self.repository.get_by_id(id)

    def get_by_syllabus(self, syllabus_id: int):
        return self.repository.get_by_syllabus_id(syllabus_id)

    def create_clo(self, data: dict):
        syllabus_id = data.get('syllabus_id')
        if not syllabus_id or not self.syllabus_repository.get_by_id(syllabus_id):
            raise ValueError('Invalid syllabus_id')
        return self.repository.create(data)

    def update_clo(self, id: int, data: dict):
        return self.repository.update(id, data)

    def delete_clo(self, id: int) -> bool:
        return self.repository.delete(id)