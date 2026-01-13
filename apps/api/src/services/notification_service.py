from typing import List
from infrastructure.repositories.notification_repository import NotificationRepository

class NotificationService:
    def __init__(self, repository: NotificationRepository, user_repository=None):
        self.repository = repository
        self.user_repository = user_repository

    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List:
        return self.repository.get_by_user(user_id, unread_only=unread_only)

    def send_notification(self, user_id: int, title: str, message: str, link: str = None, type: str = 'SYSTEM'):
        if self.user_repository and not self.user_repository.get_by_id(user_id):
             raise ValueError('User not found')
        data = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'link': link,
            'type': type,
            'is_read': False
        }
        return self.repository.create(data)

    def mark_read(self, id: int) -> bool:
        return self.repository.mark_as_read(id)

    def mark_all_read(self, user_id: int):
        return self.repository.mark_all_as_read(user_id)