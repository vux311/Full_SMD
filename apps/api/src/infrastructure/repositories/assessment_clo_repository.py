from typing import List
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.assessment_clo_model import AssessmentClo
from infrastructure.models.syllabus_clo_model import SyllabusClo

class AssessmentCloRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def add_mapping(self, component_id: int, syllabus_clo_id: int) -> AssessmentClo:
        mapping = AssessmentClo(assessment_component_id=component_id, syllabus_clo_id=syllabus_clo_id)
        self.session.add(mapping)
        self.session.commit()
        return mapping

    def remove_mapping(self, component_id: int, syllabus_clo_id: int) -> bool:
        mapping = self.session.query(AssessmentClo).filter_by(assessment_component_id=component_id, syllabus_clo_id=syllabus_clo_id).first()
        if not mapping:
            return False
        self.session.delete(mapping)
        self.session.commit()
        return True

    def get_clos_by_component(self, component_id: int) -> List[SyllabusClo]:
        mappings = self.session.query(AssessmentClo).filter_by(assessment_component_id=component_id).all()
        return [m.syllabus_clo for m in mappings]