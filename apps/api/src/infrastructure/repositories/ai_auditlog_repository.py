from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.ai_auditlog_model import AiAuditLog

class AiAuditLogRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def create(self, syllabus_id: int, action: str, input_tokens: int, output_tokens: int):
        log = AiAuditLog(syllabus_id=syllabus_id, action=action, input_tokens=input_tokens, output_tokens=output_tokens)
        self.session.add(log)
        self.session.commit()
        return log