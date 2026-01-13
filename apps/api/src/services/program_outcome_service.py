from typing import List
from infrastructure.repositories.program_outcome_repository import ProgramOutcomeRepository

class ProgramOutcomeService:
    def __init__(self, repository: ProgramOutcomeRepository, program_repository=None):
        self.repository = repository
        self.program_repository = program_repository

    def list_by_program(self, program_id: int) -> List:
        return self.repository.get_by_program_id(program_id)

    def create_plo(self, data: dict):
        program_id = data.get('program_id')
        if not program_id or not self.program_repository.get_by_id(program_id):
            raise ValueError('Invalid program_id')
        return self.repository.create(data)

    def update_plo(self, id: int, data: dict):
        return self.repository.update(id, data)

    def delete_plo(self, id: int) -> bool:
        return self.repository.delete(id)