from typing import List, Optional
from infrastructure.repositories.syllabus_repository import SyllabusRepository
from utils.logging_config import get_logger

logger = get_logger(__name__)

class SyllabusService:
    def __init__(self, repository: SyllabusRepository,
                 subject_repository=None,
                 program_repository=None,
                 academic_year_repository=None,
                 user_repository=None,
                 workflow_log_repository=None,
                 syllabus_clo_repository=None,
                 syllabus_material_repository=None,
                 teaching_plan_repository=None,
                 assessment_scheme_repository=None,
                 assessment_component_repository=None,
                 rubric_repository=None,
                 assessment_clo_repository=None):
        self.repository = repository
        self.subject_repository = subject_repository
        self.program_repository = program_repository
        self.academic_year_repository = academic_year_repository
        self.user_repository = user_repository
        self.workflow_log_repository = workflow_log_repository
        self.syllabus_clo_repository = syllabus_clo_repository
        self.syllabus_material_repository = syllabus_material_repository
        self.teaching_plan_repository = teaching_plan_repository
        self.assessment_scheme_repository = assessment_scheme_repository
        self.assessment_component_repository = assessment_component_repository
        self.rubric_repository = rubric_repository
        self.assessment_clo_repository = assessment_clo_repository

    def list_syllabuses(self) -> List:
        logger.info("Listing all syllabuses")
        try:
            result = self.repository.get_all()
            logger.info(f"Retrieved {len(result)} syllabuses")
            return result
        except Exception as e:
            logger.error(f"Error listing syllabuses: {str(e)}", exc_info=True)
            raise
    
    def list_syllabuses_paginated(self, page: int, page_size: int):
        """Get paginated list of syllabuses"""
        logger.info(f"Listing syllabuses - page {page}, size {page_size}")
        try:
            items, total = self.repository.get_all_paginated(page, page_size)
            logger.info(f"Retrieved {len(items)} of {total} syllabuses")
            return items, total
        except Exception as e:
            logger.error(f"Error listing paginated syllabuses: {str(e)}", exc_info=True)
            raise

    def get_syllabus(self, id: int):
        return self.repository.get_by_id(id)

    def get_syllabus_details(self, id: int):
        return self.repository.get_details(id)

    def get_by_subject(self, subject_id: int):
        return self.repository.get_by_subject_id(subject_id)

    def create_syllabus(self, data: dict):
        import json
        
        # Extract child data
        clos_data = data.pop('clos', [])
        materials_data = data.pop('materials', [])
        plans_data = data.pop('teaching_plans', [])
        schemes_data = data.pop('assessment_schemes', [])

        # Handle time_allocation (Dict -> JSON String)
        if 'time_allocation' in data and isinstance(data['time_allocation'], dict):
            data['time_allocation'] = json.dumps(data['time_allocation'])

        # Validate Foreign Keys
        subject_id = data.get('subject_id')
        if not subject_id or not self.subject_repository.get_by_id(subject_id):
            raise ValueError('Invalid subject_id')
        program_id = data.get('program_id')
        if not program_id or not self.program_repository.get_by_id(program_id):
            raise ValueError('Invalid program_id')
        academic_year_id = data.get('academic_year_id')
        if not academic_year_id or not self.academic_year_repository.get_by_id(academic_year_id):
            raise ValueError('Invalid academic_year_id')
        lecturer_id = data.get('lecturer_id')
        if not lecturer_id or not self.user_repository.get_by_id(lecturer_id):
            raise ValueError('Invalid lecturer_id')

        # Create Header
        data.setdefault('status', 'DRAFT')
        new_syllabus = self.repository.create(data)
        sid = new_syllabus.id

        # 1. Save CLOs
        if self.syllabus_clo_repository:
            for item in clos_data:
                item['syllabus_id'] = sid
                self.syllabus_clo_repository.create(item)

        # 2. Save Materials
        if self.syllabus_material_repository:
            for item in materials_data:
                item['syllabus_id'] = sid
                self.syllabus_material_repository.create(item)

        # 3. Save Teaching Plans
        if self.teaching_plan_repository:
            for item in plans_data:
                item['syllabus_id'] = sid
                self.teaching_plan_repository.create(item)

        # 4. Save Assessment Schemes (Nested)
        if self.assessment_scheme_repository:
            for scheme in schemes_data:
                components = scheme.pop('components', [])
                scheme['syllabus_id'] = sid
                new_scheme = self.assessment_scheme_repository.create(scheme)
                if self.assessment_component_repository:
                    for comp in components:
                        rubrics = comp.pop('rubrics', [])
                        comp['scheme_id'] = new_scheme.id
                        new_comp = self.assessment_component_repository.create(comp)
                        if self.rubric_repository:
                            for rub in rubrics:
                                rub['component_id'] = new_comp.id
                                self.rubric_repository.create(rub)

        return new_syllabus

    def update_syllabus(self, id: int, data: dict):
        # Check current status before allowing update
        s = self.repository.get_by_id(id)
        if not s:
            return None
        if s.status not in ('DRAFT', 'REJECTED'):
            raise ValueError(f"Cannot update syllabus in {s.status} status")
        return self.repository.update(id, data)

    def delete_syllabus(self, id: int) -> bool:
        return self.repository.delete(id)

    # Workflow methods
    def submit_syllabus(self, id: int, user_id: int):
        """Submit syllabus for evaluation. Can only submit from DRAFT or REJECTED status."""
        s = self.repository.get_by_id(id)
        if not s:
            return None
        
        current_status = (s.status or '').upper()
        # Only allow submission from DRAFT or REJECTED states
        valid_states = ('DRAFT', 'REJECTED')
        
        if current_status not in valid_states:
            raise ValueError(
                f'Cannot submit syllabus in {current_status} status. '
                f'Valid states for submission: {valid_states}'
            )
        
        from_status = s.status
        updated = self.repository.update(id, {'status': 'PENDING'})
        if self.workflow_log_repository:
            self.workflow_log_repository.create({
                'syllabus_id': id,
                'actor_id': user_id,
                'action': 'SUBMIT',
                'from_status': from_status,
                'to_status': 'PENDING',
                'comment': None
            })
        return updated

    def evaluate_syllabus(self, id: int, user_id: int, action: str, comment: Optional[str] = None):
        """Evaluate syllabus. Can only evaluate PENDING syllabuses."""
        s = self.repository.get_by_id(id)
        if not s:
            return None
        
        action = action.upper()
        if action not in ('APPROVE', 'REJECT'):
            raise ValueError(f'Invalid action: {action}. Must be APPROVE or REJECT')
        
        # Check current status
        if s.status != 'PENDING':
            raise ValueError(
                f'Can only evaluate PENDING syllabuses. Current status: {s.status}'
            )
        
        from_status = s.status
        if action == 'APPROVE':
            new_status = 'APPROVED'
        else:  # REJECT
            if not comment:
                raise ValueError('Comment is required when rejecting')
            new_status = 'DRAFT'
        
        updated = self.repository.update(id, {'status': new_status})
        if self.workflow_log_repository:
            self.workflow_log_repository.create({
                'syllabus_id': id,
                'actor_id': user_id,
                'action': action,
                'from_status': from_status,
                'to_status': new_status,
                'comment': comment
            })
        return updated

    def get_workflow_logs(self, syllabus_id: int):
        if not self.workflow_log_repository:
            return []
        return self.workflow_log_repository.get_by_syllabus_id(syllabus_id)