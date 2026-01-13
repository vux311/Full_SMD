from typing import List
from infrastructure.repositories.subject_relationship_repository import SubjectRelationshipRepository

class SubjectRelationshipService:
    def __init__(self, repository: SubjectRelationshipRepository, subject_repository=None):
        self.repository = repository
        self.subject_repository = subject_repository

    def get_relationships(self, subject_id: int) -> List:
        return self.repository.get_by_subject(subject_id)

    def add_relationship(self, data: dict):
        subject_id = data.get('subject_id')
        related_id = data.get('related_subject_id')
        
        if subject_id == related_id:
            raise ValueError('Subject cannot be related to itself')
        
        if not self.subject_repository.get_by_id(subject_id):
            raise ValueError('Invalid subject_id')
        if not self.subject_repository.get_by_id(related_id):
            raise ValueError('Invalid related_subject_id')
            
        return self.repository.create(data)

    def remove_relationship(self, id: int) -> bool:
        return self.repository.delete(id)