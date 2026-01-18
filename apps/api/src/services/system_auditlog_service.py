from infrastructure.repositories.system_auditlog_repository import SystemAuditLogRepository

class SystemAuditLogService:
    def __init__(self, repository: SystemAuditLogRepository):
        self.repository = repository

    def create_log(self, user_id: int, action_type: str, resource_target: str = None,
                   ip_address: str = None, user_agent: str = None, details: str = None):
        """Create a new audit log entry"""
        return self.repository.create(
            user_id=user_id,
            action_type=action_type,
            resource_target=resource_target,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )

    def list_logs(self, limit: int = 100):
        """Get recent audit logs"""
        return self.repository.list_logs(limit)

    def get_user_logs(self, user_id: int, limit: int = 50):
        """Get audit logs for a specific user"""
        return self.repository.get_by_user(user_id, limit)
