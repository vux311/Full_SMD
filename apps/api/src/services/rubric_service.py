from typing import List, Optional
from infrastructure.repositories.rubric_repository import RubricRepository

class RubricService:
    def __init__(self, repository: RubricRepository, component_repository=None):
        self.repository = repository
        self.component_repository = component_repository

    def list_rubrics_for_component(self, component_id: int) -> List:
        return self.repository.get_by_component_id(component_id)

    def get_rubric(self, id: int):
        return self.repository.get_by_id(id)

    def create_rubric(self, data: dict):
        component_id = data.get('component_id')
        if not component_id or not self.component_repository.get_by_id(component_id):
            raise ValueError('Invalid component_id')
        return self.repository.create(data)

    def update_rubric(self, id: int, data: dict):
        return self.repository.update(id, data)

    def delete_rubric(self, id: int) -> bool:
        return self.repository.delete(id)