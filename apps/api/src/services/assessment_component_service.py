from typing import Optional
from infrastructure.repositories.assessment_component_repository import AssessmentComponentRepository

class AssessmentComponentService:
    def __init__(self, repository: AssessmentComponentRepository, scheme_repository=None):
        self.repository = repository
        self.scheme_repository = scheme_repository

    def get_component(self, id: int):
        return self.repository.get_by_id(id)

    def create_component(self, data: dict):
        scheme_id = data.get('scheme_id')
        if not scheme_id or not self.scheme_repository.get_by_id(scheme_id):
            raise ValueError('Invalid scheme_id')
        return self.repository.create(data)

    def update_component(self, id: int, data: dict):
        return self.repository.update(id, data)

    def delete_component(self, id: int) -> bool:
        return self.repository.delete(id)