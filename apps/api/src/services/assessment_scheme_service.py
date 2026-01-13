from typing import List, Optional
from infrastructure.repositories.assessment_scheme_repository import AssessmentSchemeRepository

class AssessmentSchemeService:
    def __init__(self, repository: AssessmentSchemeRepository, syllabus_repository=None):
        self.repository = repository
        self.syllabus_repository = syllabus_repository

    def list_schemes_for_syllabus(self, syllabus_id: int) -> List:
        return self.repository.get_by_syllabus_id(syllabus_id)

    def get_scheme(self, id: int):
        return self.repository.get_by_id(id)

    def create_scheme(self, data: dict):
        syllabus_id = data.get('syllabus_id')
        if not syllabus_id or not self.syllabus_repository.get_by_id(syllabus_id):
            raise ValueError('Invalid syllabus_id')
        return self.repository.create(data)

    def update_scheme(self, id: int, data: dict):
        return self.repository.update(id, data)

    def delete_scheme(self, id: int) -> bool:
        return self.repository.delete(id)