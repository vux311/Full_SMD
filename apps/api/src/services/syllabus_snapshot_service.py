from infrastructure.repositories.syllabus_snapshot_repository import SyllabusSnapshotRepository
from typing import Dict, Any, Optional

class SyllabusSnapshotService:
    def __init__(self, repository: SyllabusSnapshotRepository, ai_service=None, syllabus_repository=None):
        self.repository = repository
        self.ai_service = ai_service
        self.syllabus_repository = syllabus_repository

    def create_snapshot(self, syllabus_id: int, version: str, data: Dict[str, Any], created_by: int = None):
        """
        Creates a new snapshot of the syllabus.
        data: dictionary containing all syllabus details (CLOs, Materials, etc.)
        """
        snapshot_data = {
            'syllabus_id': syllabus_id,
            'version': version,
            'snapshot_data': data,
            'created_by': created_by
        }
        return self.repository.create(snapshot_data)

    def get_syllabus_history(self, syllabus_id: int):
        return self.repository.get_by_syllabus(syllabus_id)

    def get_snapshot(self, snapshot_id: int):
        return self.repository.get_by_id(snapshot_id)

    def compare_snapshots(self, snapshot_id_1: int, snapshot_id_2: int):
        """Compare two historical snapshots using AI"""
        s1 = self.get_snapshot(snapshot_id_1)
        s2 = self.get_snapshot(snapshot_id_2)
        
        if not s1 or not s2:
            raise ValueError("Snapshot not found")
            
        if not self.ai_service:
            return {"error": "AI Service not available"}
            
        return self.ai_service.compare_syllabuses(s1.snapshot_data, s2.snapshot_data)

    def compare_with_current(self, snapshot_id: int, current_syllabus_id: int):
        """Compare a historical snapshot with the current active syllabus"""
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            raise ValueError("Snapshot not found")
            
        if not self.syllabus_repository or not self.ai_service:
            return {"error": "Syllabus repository or AI service not available"}
            
        # We need a schema to dump the current syllabus to dict
        from api.schemas.syllabus_schema import SyllabusSchema
        current_syllabus = self.syllabus_repository.get_details(current_syllabus_id)
        if not current_syllabus:
            raise ValueError("Current syllabus not found")
            
        schema = SyllabusSchema()
        current_data = schema.dump(current_syllabus)
        
        return self.ai_service.compare_syllabuses(snapshot.snapshot_data, current_data)
