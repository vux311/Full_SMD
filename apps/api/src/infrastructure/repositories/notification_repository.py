from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.notification_model import Notification

class NotificationRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_by_user(self, user_id: int, limit: int = 20, unread_only: bool = False) -> List[Notification]:
        query = self.session.query(Notification).filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def create(self, data: dict) -> Notification:
        item = Notification(**data)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def mark_as_read(self, id: int) -> bool:
        item = self.session.query(Notification).filter_by(id=id).first()
        if not item:
            return False
        item.is_read = True
        self.session.commit()
        return True

    def mark_all_as_read(self, user_id: int):
        self.session.query(Notification).filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        self.session.commit()