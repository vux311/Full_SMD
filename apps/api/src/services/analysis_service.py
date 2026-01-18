from typing import List, Dict
from infrastructure.repositories.syllabus_repository import SyllabusRepository
from infrastructure.repositories.subject_relationship_repository import SubjectRelationshipRepository
from domain.constants import WorkflowStatus

class AnalysisService:
    def __init__(self, syllabus_repository: SyllabusRepository, 
                 rel_repository: SubjectRelationshipRepository):
        self.syllabus_repo = syllabus_repository
        self.rel_repo = rel_repository

    def get_impact_analysis(self, syllabus_id: int) -> Dict:
        """
        Analyze what other syllabuses are impacted if this syllabus changes.
        Principal/Strategic view.
        """
        syllabus = self.syllabus_repo.get_by_id(syllabus_id)
        if not syllabus:
            return None
            
        subject_id = syllabus.subject_id
        
        # 1. Find direct successors (Subjects that have THIS subject as a prerequisite)
        successors = self.rel_repo.get_successors(subject_id)
        
        impacted_subjects = []
        for rel in successors:
            # For each successor subject, find its active/published syllabus
            active_syllabus = self.syllabus_repo.get_active_by_subject(rel.subject_id)
            impacted_subjects.append({
                "subject_id": rel.subject_id,
                "subject_code": rel.subject.code if rel.subject else "N/A",
                "subject_name": rel.subject.name_vi if rel.subject else "N/A",
                "type": rel.type,
                "syllabus_status": active_syllabus.status if active_syllabus else "No Active Syllabus",
                "syllabus_id": active_syllabus.id if active_syllabus else None
            })
            
        return {
            "root_syllabus": {
                "id": syllabus.id,
                "subject_name": syllabus.subject.name_vi if syllabus.subject else "N/A",
                "version": syllabus.version
            },
            "impacted_count": len(impacted_subjects),
            "impact_level": "High" if len(impacted_subjects) > 3 else "Medium" if len(impacted_subjects) > 0 else "Low",
            "details": impacted_subjects
        }
