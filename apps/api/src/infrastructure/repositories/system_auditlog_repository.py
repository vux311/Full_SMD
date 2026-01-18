from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.system_auditlog_model import SystemAuditLog

class SystemAuditLogRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def create(self, user_id: int, action_type: str, resource_target: str = None, 
               ip_address: str = None, user_agent: str = None, details: str = None):
        """Create a new system audit log entry"""
        log = SystemAuditLog(
            user_id=user_id,
            action_type=action_type,
            resource_target=resource_target,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        self.session.add(log)
        self.session.commit()
        return log

    def list_logs(self, limit: int = 100):
        """Get recent audit logs with user information"""
        return self.session.query(SystemAuditLog)\
            .order_by(SystemAuditLog.created_at.desc())\
            .limit(limit)\
            .all()

    def get_by_user(self, user_id: int, limit: int = 50):
        """Get audit logs for a specific user"""
        return self.session.query(SystemAuditLog)\
            .filter(SystemAuditLog.user_id == user_id)\
            .order_by(SystemAuditLog.created_at.desc())\
            .limit(limit)\
            .all()
