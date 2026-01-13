from typing import List
from infrastructure.repositories.student_subscription_repository import StudentSubscriptionRepository
from infrastructure.repositories.student_report_repository import StudentReportRepository

class StudentService:
    def __init__(self, sub_repo: StudentSubscriptionRepository, report_repo: StudentReportRepository):
        self.sub_repo = sub_repo
        self.report_repo = report_repo

    def subscribe(self, user_id: int, subject_id: int):
        return self.sub_repo.create(user_id, subject_id)

    def unsubscribe(self, user_id: int, subject_id: int):
        return self.sub_repo.delete(user_id, subject_id)

    def get_subscriptions(self, user_id: int):
        return self.sub_repo.get_by_student(user_id)

    def report_syllabus(self, user_id: int, syllabus_id: int, content: str):
        return self.report_repo.create({'student_id': user_id, 'syllabus_id': syllabus_id, 'content': content})

    def list_reports(self):
        return self.report_repo.get_all()

    def resolve_report(self, id: int, status: str, note: str = None):
        return self.report_repo.update_status(id, status, note)