from typing import List
from infrastructure.repositories.clo_plo_mapping_repository import CloPloMappingRepository

class CloPloMappingService:
    def __init__(self, repository: CloPloMappingRepository, syllabus_clo_repository=None, program_outcome_repository=None):
        self.repository = repository
        self.syllabus_clo_repository = syllabus_clo_repository
        self.program_outcome_repository = program_outcome_repository

    def get_by_clo(self, clo_id: int) -> List:
        return self.repository.get_by_syllabus_clo(clo_id)

    def create_mapping(self, data: dict):
        clo_id = data.get('syllabus_clo_id')
        plo_id = data.get('program_plo_id')
        
        if not self.syllabus_clo_repository.get_by_id(clo_id):
            raise ValueError('Invalid syllabus_clo_id')
        if not self.program_outcome_repository.get_by_id(plo_id):
            raise ValueError('Invalid program_plo_id')
            
        return self.repository.create(data)

    def delete_mapping(self, id: int) -> bool:
        return self.repository.delete(id)