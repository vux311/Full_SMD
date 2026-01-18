from typing import List
from infrastructure.repositories.notification_repository import NotificationRepository
from utils.socket_io import notify_user

class NotificationService:
    def __init__(self, repository: NotificationRepository, user_repository=None, email_service=None):
        self.repository = repository
        self.user_repository = user_repository
        self.email_service = email_service

    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List:
        return self.repository.get_by_user(user_id, unread_only=unread_only)

    def send_notification(self, user_id: int, title: str, message: str, link: str = None, type: str = 'SYSTEM', event_name: str = 'new_notification', send_email: bool = True):
        user = None
        if self.user_repository:
             user = self.user_repository.get_by_id(user_id)
             if not user:
                 raise ValueError('User not found')
        
        data = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'link': link,
            'type': type,
            'is_read': False
        }
        
        # Save to DB
        notif = self.repository.create(data)
        
        # Emit via SocketIO for real-time update
        notify_user(user_id, event_name, {
            'id': notif.id,
            'title': title,
            'message': message,
            'link': link,
            'type': type,
            'is_read': False,
            'created_at': notif.created_at.isoformat() if hasattr(notif, 'created_at') and notif.created_at else None
        })

        # Send Email if requested and service available
        if send_email and self.email_service and user:
            # We don't want to block the response if email sending takes time
            # Ideally this should be a background task (Celery), but for now we do it inline
            # with safe try-except in the EmailService
            self.email_service.notify_user(user, title, message)
        
        return notif

    def notify_roles(self, roles: List[str], title: str, message: str, link: str = None, type: str = 'SYSTEM', event_name: str = 'new_notification'):
        """Send notification to all users belonging to specific roles"""
        if not self.user_repository:
            return
            
        users = self.user_repository.get_all()
        target_users = []
        for u in users:
            u_roles = [r.name for r in u.roles] if hasattr(u, 'roles') else []
            if any(role in u_roles for role in roles):
                target_users.append(u)
        
        for u in target_users:
            self.send_notification(u.id, title, message, link, type, event_name)

    def mark_read(self, id: int) -> bool:
        return self.repository.mark_as_read(id)

    def mark_all_read(self, user_id: int):
        return self.repository.mark_all_as_read(user_id)