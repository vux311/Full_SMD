from typing import List
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.student_subscription_model import StudentSubscription

class StudentSubscriptionRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def create(self, user_id: int, subject_id: int):
        # Check exists
        exists = self.session.query(StudentSubscription).filter_by(student_id=user_id, subject_id=subject_id).first()
        if exists: return exists
        
        item = StudentSubscription(student_id=user_id, subject_id=subject_id)
        self.session.add(item)
        self.session.commit()
        return item

    def delete(self, user_id: int, subject_id: int):
        item = self.session.query(StudentSubscription).filter_by(student_id=user_id, subject_id=subject_id).first()
        if item:
            self.session.delete(item)
            self.session.commit()
            return True
        return False

    def get_by_student(self, user_id: int) -> List[StudentSubscription]:
        return self.session.query(StudentSubscription).filter_by(student_id=user_id).all()