from typing import List, Optional
from infrastructure.repositories.program_repository import ProgramRepository

class ProgramService:
    def __init__(self, repository: ProgramRepository):
        self.repository = repository

    def list_programs(self) -> List:
        return self.repository.get_all()

    def get_program(self, id: int):
        return self.repository.get_by_id(id)

    def create_program(self, data: dict):
        return self.repository.create(data)

    def update_program(self, id: int, data: dict):
        return self.repository.update(id, data)

    def delete_program(self, id: int) -> bool:
        return self.repository.delete(id)