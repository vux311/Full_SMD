from typing import List
from infrastructure.repositories.syllabus_comment_repository import SyllabusCommentRepository

class SyllabusCommentService:
    def __init__(self, repository: SyllabusCommentRepository, syllabus_repository=None, user_repository=None):
        self.repository = repository
        self.syllabus_repository = syllabus_repository
        self.user_repository = user_repository

    def get_comments(self, syllabus_id: int) -> List:
        return self.repository.get_by_syllabus(syllabus_id)

    def add_comment(self, data: dict):
        syllabus_id = data.get('syllabus_id')
        user_id = data.get('user_id')
        
        if not self.syllabus_repository.get_by_id(syllabus_id):
            raise ValueError('Invalid syllabus_id')
        if not self.user_repository.get_by_id(user_id):
            raise ValueError('Invalid user_id')
            
        return self.repository.create(data)

    def resolve_comment(self, id: int):
        return self.repository.update(id, {'is_resolved': True})

    def delete_comment(self, id: int) -> bool:
        return self.repository.delete(id)