from typing import List
from infrastructure.repositories.subject_relationship_repository import SubjectRelationshipRepository

class SubjectRelationshipService:
    def __init__(self, repository: SubjectRelationshipRepository, subject_repository=None):
        self.repository = repository
        self.subject_repository = subject_repository

    def get_relationships(self, subject_id: int) -> List:
        return self.repository.get_by_subject(subject_id)

    def get_tree(self, subject_id: int):
        """
        Get recursive pre-reqs and successors for a subject tree view.
        Uses a visited set to avoid infinite loops in cyclical dependencies.
        """
        prerequisites = []
        successors = []
        
        # Helper for recursive search
        def find_prereqs(sid, visited):
            if sid in visited:
                return
            visited.add(sid)
            
            rels = self.repository.get_by_subject(sid)
            for r in rels:
                if r not in prerequisites:
                    prerequisites.append(r)
                if r.related_subject_id:
                    find_prereqs(r.related_subject_id, visited)

        def find_successors(sid, visited):
            if sid in visited:
                return
            visited.add(sid)
            
            rels = self.repository.get_successors(sid)
            for r in rels:
                if r not in successors:
                    successors.append(r)
                if r.subject_id:
                    find_successors(r.subject_id, visited)

        find_prereqs(subject_id, set())
        # Reset visited for successors search
        find_successors(subject_id, set())
        
        return {
            "prerequisites": prerequisites,
            "successors": successors
        }

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