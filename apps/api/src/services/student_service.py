from typing import List
from infrastructure.repositories.student_subscription_repository import StudentSubscriptionRepository
from infrastructure.repositories.student_report_repository import StudentReportRepository
from infrastructure.repositories.user_repository import UserRepository
from services.notification_service import NotificationService

class StudentService:
    def __init__(self, 
                 sub_repo: StudentSubscriptionRepository, 
                 report_repo: StudentReportRepository,
                 user_repo: UserRepository = None,
                 notification_service: NotificationService = None):
        self.sub_repo = sub_repo
        self.report_repo = report_repo
        self.user_repo = user_repo
        self.notification_service = notification_service

    def subscribe(self, user_id: int, subject_id: int):
        return self.sub_repo.create(user_id, subject_id)

    def unsubscribe(self, user_id: int, subject_id: int):
        return self.sub_repo.delete(user_id, subject_id)

    def get_subscriptions(self, user_id: int):
        return self.sub_repo.get_by_student(user_id)

    def report_syllabus(self, user_id: int, syllabus_id: int, content: str):
        report = self.report_repo.create({'student_id': user_id, 'syllabus_id': syllabus_id, 'content': content})
        
        # Notify admins and relevant staff
        if self.notification_service and self.user_repo:
            try:
                # Notify Admin and Academic Affairs
                targets = []
                targets.extend(self.user_repo.get_users_by_role('Admin'))
                targets.extend(self.user_repo.get_users_by_role('Academic Affairs'))
                targets.extend(self.user_repo.get_users_by_role('AA'))
                
                # Unique users
                target_ids = set()
                
                student = self.user_repo.get_by_id(user_id)
                student_name = student.full_name if student else "Một sinh viên"
                
                for staff in targets:
                    if staff.id not in target_ids:
                        self.notification_service.send_notification(
                            user_id=staff.id,
                            title="Phản hồi mới từ sinh viên",
                            message=f"{student_name} vừa gửi một phản hồi về nội dung đề cương.",
                            link="/admin/reports",
                            type="WARNING"
                        )
                        target_ids.add(staff.id)
            except Exception as e:
                print(f"Error sending report notification: {e}")
                
        return report

    def list_reports(self):
        return self.report_repo.get_all()

    def resolve_report(self, id: int, status: str, note: str = None):
        report = self.report_repo.update_status(id, status, note)
        
        # Notify student
        if report and self.notification_service:
            try:
                status_vi = "đã được xử lý" if status == "RESOLVED" else "đã bị từ chối"
                self.notification_service.send_notification(
                    user_id=report.student_id,
                    title="Cập nhật phản hồi",
                    message=f"Phản hồi của bạn về một đề cương học phần {status_vi}.",
                    link="/dashboard",
                    type="INFO"
                )
            except Exception as e:
                print(f"Error sending resolve notification: {e}")
                
        return report
