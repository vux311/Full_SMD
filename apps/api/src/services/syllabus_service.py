from typing import List, Optional
import json
from datetime import datetime, timedelta

from infrastructure.models.syllabus_model import Syllabus
from infrastructure.models.syllabus_clo_model import SyllabusClo
from infrastructure.models.clo_plo_mapping_model import CloPloMapping
from infrastructure.models.syllabus_material_model import SyllabusMaterial
from infrastructure.models.teaching_plan_model import TeachingPlan
from infrastructure.models.assessment_scheme_model import AssessmentScheme
from infrastructure.models.assessment_component_model import AssessmentComponent
from infrastructure.models.rubric_model import Rubric
from infrastructure.models.program_outcome_model import ProgramOutcome
from infrastructure.models.workflow_log_model import WorkflowLog
from infrastructure.models.student_subscription_model import StudentSubscription

from infrastructure.repositories.syllabus_repository import SyllabusRepository
from domain.constants import WorkflowStatus
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
                 assessment_clo_repository=None,
                 notification_service=None,
                 snapshot_service=None,
                 current_workflow_repository=None,
                 clo_plo_mapping_repository=None,
                 program_outcome_repository=None,
                 search_service=None,
                 student_subscription_repository=None,
                 system_setting_service=None):
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
        self.notification_service = notification_service
        self.snapshot_service = snapshot_service
        self.current_workflow_repository = current_workflow_repository
        self.clo_plo_mapping_repository = clo_plo_mapping_repository
        self.program_outcome_repository = program_outcome_repository
        self.search_service = search_service
        self.student_subscription_repository = student_subscription_repository
        self.system_setting_service = system_setting_service

    def _index_to_search(self, syllabus):
        """Helper to index a syllabus to Elasticsearch background/silent failure"""
        if not self.search_service:
            return
        try:
            content = {
                "subject_code": syllabus.subject.code if syllabus.subject else "",
                "subject_name_vi": syllabus.subject.name_vi if syllabus.subject else "",
                "description": syllabus.description or "",
                "status": syllabus.status,
                "version": syllabus.version,
                "program_name": syllabus.program.name if syllabus.program else "",
                "academic_year": syllabus.academic_year.code if syllabus.academic_year else "",
                "content": syllabus.description or ""
            }
            self.search_service.index_syllabus(syllabus.id, content)
            logger.info(f"Indexed syllabus {syllabus.id} to search")
        except Exception as e:
            logger.warning(f"Failed to index syllabus {syllabus.id}: {e}")

    def get_kpis(self):
        """KPI Dashboard optimized with SQL Aggregation (PERF-001 & PERF-002)"""
        from sqlalchemy import func, case, text
        from infrastructure.models.syllabus_model import Syllabus
        from infrastructure.models.workflow_log_model import WorkflowLog
        from domain.constants import WorkflowStatus

        session = self.repository.session
        
        # Chỉ tính là đang chờ duyệt nếu thuộc 3 trạng thái này
        pending_list = [WorkflowStatus.PENDING_REVIEW, WorkflowStatus.PENDING_APPROVAL, WorkflowStatus.APPROVED]
        
        # PERF-002: Use SQL COUNT and CASE instead of loading all objects into memory
        stats = session.query(
            func.count(Syllabus.id).label('total'),
            func.sum(case((func.upper(Syllabus.status).in_(pending_list), 1), else_=0)).label('pending'),
            func.sum(case((func.upper(Syllabus.status) == WorkflowStatus.PUBLISHED, 1), else_=0)).label('completed')
        ).first()
        
        total = stats.total or 0
        pending = stats.pending or 0
        completed_count = stats.completed or 0
        
        # PERF-001: Aggregation directly in SQL for avg review time
        avg_hours = 0
        if self.workflow_log_repository:
            # Subquery for first SUBMIT per syllabus
            submits = session.query(
                WorkflowLog.syllabus_id,
                func.min(WorkflowLog.created_at).label('submit_time')
            ).filter(WorkflowLog.action == 'SUBMIT').group_by(WorkflowLog.syllabus_id).subquery()
            
            # Subquery for first APPROVE per syllabus
            approves = session.query(
                WorkflowLog.syllabus_id,
                func.min(WorkflowLog.created_at).label('approve_time')
            ).filter(WorkflowLog.action == 'APPROVE').group_by(WorkflowLog.syllabus_id).subquery()
            
            # Join and calculate avg duration in seconds (MSSQL DATEDIFF)
            avg_seconds = session.query(
                func.avg(func.datediff(text('second'), submits.c.submit_time, approves.c.approve_time))
            ).join(approves, submits.c.syllabus_id == approves.c.syllabus_id)\
             .filter(approves.c.approve_time > submits.c.submit_time).scalar()
             
            if avg_seconds:
                avg_hours = float(avg_seconds) / 3600
        
        return {
            "total_syllabuses": total,
            "pending_count": int(pending),
            "completed_count": int(completed_count),
            "avg_review_time_hours": round(avg_hours, 1),
            "compliance_rate": round((total - pending) / total * 100, 1) if total > 0 else 0
        }

    def list_syllabuses(self, filters: dict = None) -> List:
        logger.info(f"Listing all syllabuses - filters: {filters}")
        try:
            result = self.repository.get_all(filters=filters)
            logger.info(f"Retrieved {len(result)} syllabuses")
            return result
        except Exception as e:
            logger.error(f"Error listing syllabuses: {str(e)}", exc_info=True)
            raise

    def list_public_syllabuses(self, filters: dict = None) -> List:
        """New method for public access - Yuri Refactor Point 2"""
        logger.info(f"Listing public syllabuses - filters: {filters}")
        try:
            result = self.repository.get_public_syllabuses(filters=filters)
            logger.info(f"Retrieved {len(result)} public syllabuses")
            return result
        except Exception as e:
            logger.error(f"Error listing public syllabuses: {str(e)}", exc_info=True)
            raise

    def list_syllabuses_paginated(self, page: int, page_size: int, filters: dict = None):
        """Get paginated list of syllabuses"""
        logger.info(f"Listing syllabuses - page {page}, size {page_size}, filters: {filters}")
        try:
            items, total = self.repository.get_all_paginated(page, page_size, filters=filters)
            logger.info(f"Retrieved {len(items)} of {total} syllabuses")
            return items, total
        except Exception as e:
            logger.error(f"Error listing paginated syllabuses: {str(e)}", exc_info=True)
            raise

    def check_workflow_deadlines(self):
        """Check all active workflows for overdue deadlines and send notifications."""
        if not self.current_workflow_repository or not self.notification_service:
            logger.warning("Deadline checker: Missing repository or notification service")
            return 0
        
        overdue_items = self.current_workflow_repository.get_overdue()
        count = 0
        for item in overdue_items:
            # Notify stakeholders based on state
            s = self.repository.get_by_id(item.syllabus_id)
            if not s: continue
            
            roles_to_notify = []
            if item.state == WorkflowStatus.PENDING_REVIEW:
                roles_to_notify = ['Head of Dept', 'Admin']
            elif item.state == WorkflowStatus.PENDING_APPROVAL:
                roles_to_notify = ['Academic Affairs', 'AA', 'Admin']
            elif item.state == WorkflowStatus.APPROVED:
                roles_to_notify = ['Principal', 'Admin']
            
            if roles_to_notify:
                self.notification_service.notify_roles(
                    roles=roles_to_notify,
                    title='CẢNH BÁO QUÁ HẠN DUYỆT',
                    message=f'Đề cương môn {s.subject.code if s.subject else "N/A"} ({item.state}) đã quá hạn duyệt ({item.due_date.strftime("%d/%m/%Y")}).',
                    link=f'/syllabus/{item.syllabus_id}',
                    event_name='workflow_overdue'
                )
                count += 1
                logger.info(f"Sent overdue notification for syllabus {item.syllabus_id}")
        
        return count

    def get_syllabus(self, id: int):
        return self.repository.get_by_id(id)

    def get_syllabus_details(self, id: int):
        return self.repository.get_details(id)

    def get_by_subject(self, subject_id: int):
        return self.repository.get_by_subject_id(subject_id)

    def _validate_assessment_weights(self, schemes_data: List):
        """Ensure each assessment scheme total weight is 100%"""
        if not schemes_data:
            return
            
        for scheme in schemes_data:
            components = scheme.get('components', [])
            total_weight = sum([float(c.get('weight', 0)) for c in components])
            # Use a small epsilon for float comparison
            if abs(total_weight - 100.0) > 0.1:
                scheme_name = scheme.get('name', 'phương pháp đánh giá')
                raise ValueError(f'Tổng trọng số của {scheme_name} phải bằng 100% (hiện tại: {total_weight}%).')

    def create_syllabus(self, data: dict):
        import json
        from sqlalchemy.exc import IntegrityError
        from infrastructure.models.syllabus_model import Syllabus
        from infrastructure.models.syllabus_clo_model import SyllabusClo
        
        # Extract child data
        clos_data = data.pop('clos', [])
        materials_data = data.pop('materials', [])
        plans_data = data.pop('teaching_plans', [])
        schemes_data = data.pop('assessment_schemes', [])

        # Strict weight validation for non-drafts
        target_status = data.get('status', 'DRAFT').upper()
        if target_status != 'DRAFT':
            self._validate_assessment_weights(schemes_data)

        # Process JSON fields
        if 'time_allocation' in data and data['time_allocation'] is not None:
            if not isinstance(data['time_allocation'], str):
                data['time_allocation'] = json.dumps(data['time_allocation'])
        
        if 'objectives' in data and data['objectives'] is not None:
            if not isinstance(data['objectives'], str):
                data['objectives'] = json.dumps(data['objectives'])

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
        
        # Check for duplicate syllabus (same combo + same status)
        target_status = data.get('status', 'DRAFT')
        existing = self.repository.session.query(Syllabus).filter_by(
            subject_id=subject_id,
            program_id=program_id,
            academic_year_id=academic_year_id,
            status=target_status
        ).first()
        
        if existing:
            subject = self.subject_repository.get_by_id(subject_id)
            status_map = {'DRAFT': 'bản nháp', 'APPROVED': 'bản đã duyệt', 'PENDING': 'bản chờ duyệt', 'REJECTED': 'bản bị từ chối'}
            status_vn = status_map.get(existing.status, existing.status)
            raise ValueError(f'Đã tồn tại một {status_vn} cho môn {subject.name_vi if subject else "này"} trong chương trình và năm học này (ID: {existing.id}).')

        # Filter data to only include valid columns for Syllabus model
        valid_columns = [c.key for c in Syllabus.__table__.columns]
        syllabus_data = {k: v for k, v in data.items() if k in valid_columns}
        
        # Use transaction to ensure atomicity
        try:
            # Create Header (don't commit yet to allow nested children)
            syllabus_data.setdefault('status', 'DRAFT')
            new_syllabus = Syllabus(**syllabus_data)
            self.repository.session.add(new_syllabus)
            self.repository.session.flush() # Get ID without committing
            sid = new_syllabus.id
            logger.info(f"Created syllabus header with ID: {sid}")

            # 1. Save CLOs
            if self.syllabus_clo_repository:
                for item in clos_data:
                    # Capture new 'mappings' field from frontend
                    mappings_data = item.pop('mappings', []) or []
                    
                    # Capture legacy mappings format
                    raw_plo_mappings = item.pop('plo_mappings_raw', {}) or item.pop('plo_mappings', {}) or item.pop('ploMappings', {})
                    
                    # Standardize legacy formats to dict {plo_code: level}
                    legacy_plo_mappings = {}
                    if isinstance(raw_plo_mappings, list):
                        for m in raw_plo_mappings:
                            if isinstance(m, dict) and ('code' in m or 'ploCode' in m) and 'level' in m:
                                code = m.get('code') or m.get('ploCode')
                                legacy_plo_mappings[code] = m['level']
                    elif isinstance(raw_plo_mappings, dict):
                        legacy_plo_mappings = raw_plo_mappings
                    
                    item['syllabus_id'] = sid
                    # Create CLO without committing
                    new_clo = self.syllabus_clo_repository.create(item, commit=False)
                    
                    # Save PLO mappings
                    if self.clo_plo_mapping_repository:
                        # Priority 1: Use explicit mappings (program_plo_id + level)
                        if mappings_data:
                            for m in mappings_data:
                                if m.get('program_plo_id'):
                                    self.clo_plo_mapping_repository.create({
                                        'syllabus_clo_id': new_clo.id,
                                        'program_plo_id': m.get('program_plo_id'),
                                        'level': m.get('level', 'I')
                                    }, commit=False)
                        
                        # Priority 2: Use legacy mappings (plo_code) if no explicit ones provided
                        elif legacy_plo_mappings and self.program_outcome_repository:
                            from infrastructure.models.program_outcome_model import ProgramOutcome
                            for plo_code, level in legacy_plo_mappings.items():
                                if not level: continue
                                
                                # Clean level (ensure it's I, R, M, or A)
                                clean_level = str(level).strip().upper()[0] if level else "I"
                                if clean_level not in ('I', 'R', 'M', 'A'):
                                    # AI sometimes sends H, M, L. Map them to IRMA
                                    ai_to_irma = {'H': 'M', 'M': 'R', 'L': 'I'}
                                    clean_level = ai_to_irma.get(clean_level, 'I')
                                
                                plo = self.program_outcome_repository.session.query(ProgramOutcome).filter_by(
                                    program_id=program_id, code=plo_code
                                ).first()
                                
                                if plo:
                                    self.clo_plo_mapping_repository.create({
                                        'syllabus_clo_id': new_clo.id,
                                        'program_plo_id': plo.id,
                                        'level': clean_level
                                    }, commit=False)

            # 2. Save Materials
            if self.syllabus_material_repository:
                for item in materials_data:
                    item['syllabus_id'] = sid
                    self.syllabus_material_repository.create(item, commit=False)

            # 3. Save Teaching Plans
            if self.teaching_plan_repository:
                for item in plans_data:
                    item['syllabus_id'] = sid
                    self.teaching_plan_repository.create(item, commit=False)

            # 4. Save Assessment Schemes (Nested)
            if self.assessment_scheme_repository:
                for scheme in schemes_data:
                    components = scheme.pop('components', [])
                    scheme['syllabus_id'] = sid
                    new_scheme = self.assessment_scheme_repository.create(scheme, commit=False)
                    if self.assessment_component_repository:
                        for comp in components:
                            rubrics = comp.pop('rubrics', [])
                            criteria = comp.pop('criteria', None)
                            clo_ids = comp.pop('clo_ids', [])
                            
                            # Handle clo_ids if it's a string
                            final_clo_ids = []
                            if isinstance(clo_ids, str):
                                codes = [c.strip() for c in clo_ids.split(',') if c.strip()]
                                for code in codes:
                                    existing_clo = self.repository.session.query(SyllabusClo).filter_by(
                                        syllabus_id=sid, code=code
                                    ).first()
                                    if existing_clo:
                                        final_clo_ids.append(existing_clo.id)
                            elif isinstance(clo_ids, list):
                                for cid in clo_ids:
                                    if isinstance(cid, int):
                                        final_clo_ids.append(cid)
                                    elif isinstance(cid, str):
                                        existing_clo = self.repository.session.query(SyllabusClo).filter_by(
                                            syllabus_id=sid, code=cid
                                        ).first()
                                        if existing_clo:
                                            final_clo_ids.append(existing_clo.id)

                            # Remove fields not in AssessmentComponent model
                            comp_data = {
                                'name': comp.get('name'),
                                'method': comp.get('method'),
                                'criteria': criteria,
                                'weight': comp.get('weight'),
                                'scheme_id': new_scheme.id
                            }
                            new_comp = self.assessment_component_repository.create(comp_data, commit=False)
                            
                            # Create rubric if criteria provided
                            if criteria and self.rubric_repository:
                                self.rubric_repository.create({
                                    'component_id': new_comp.id,
                                    'criteria': criteria,
                                    'max_score': 10.0
                                }, commit=False)
                            
                            # Create rubric list if provided
                            if rubrics and self.rubric_repository:
                                for rub in rubrics:
                                    rub['component_id'] = new_comp.id
                                    self.rubric_repository.create(rub, commit=False)
                                    
                            # Create CLO mappings
                            if final_clo_ids and self.assessment_clo_repository:
                                for clo_id in final_clo_ids:
                                    self.assessment_clo_repository.add_mapping(new_comp.id, clo_id, commit=False)
            
            # Commit all at once
            self.repository.session.commit()
            logger.info(f"Successfully created syllabus {sid} with all children")
            
            # Non-blocking index to search
            self._index_to_search(new_syllabus)
            
            return new_syllabus
            
        except IntegrityError as e:
            self.repository.session.rollback()
            logger.error(f"Integrity error creating syllabus: {str(e)}")
            raise ValueError('Lỗi ràng buộc dữ liệu. Có thể đề cương này đã tồn tại.')
        except Exception as e:
            self.repository.session.rollback()
            logger.error(f"Error creating syllabus: {str(e)}", exc_info=True)
            raise

    def update_syllabus(self, id: int, data: dict, user_id: int = None, user_role: str = None):
        import json
        from infrastructure.models.syllabus_model import Syllabus
        from infrastructure.models.syllabus_clo_model import SyllabusClo
        
        logger.info(f"Updating syllabus {id}. Data keys: {list(data.keys())}")
        
        # Check current status before allowing update - use for_update to avoid race
        s = self.repository.get_by_id(id, for_update=True)
        if not s:
            return None
        
        # SEC-001 IDOR: Check ownership
        if user_id and user_role != 'Admin':
            if s.lecturer_id != user_id:
                raise ValueError("Bạn không có quyền chỉnh sửa đề cương này (không phải owner).")
        
        current_status = (s.status or '').upper()
        # Block update if status is PUBLISHED or any other status not in DRAFT/RETURNED
        if current_status == WorkflowStatus.PUBLISHED:
            raise ValueError(f"Cannot update a PUBLISHED syllabus. Please create a new version.")
        
        if current_status not in (WorkflowStatus.DRAFT, WorkflowStatus.RETURNED):
            raise ValueError(f"Cannot update syllabus in {s.status} status. It is either pending or permanently rejected.")

        # Extract child data
        clos_data = data.pop('clos', None)
        materials_data = data.pop('materials', None)
        plans_data = data.pop('teaching_plans', None)
        schemes_data = data.pop('assessment_schemes', None)
        
        # DI-001: Validate weight BEFORE any DB operations (deletion/creation)
        if schemes_data is not None:
            self._validate_assessment_weights(schemes_data)
        
        # Process JSON fields
        if 'time_allocation' in data and data['time_allocation'] is not None:
            if not isinstance(data['time_allocation'], str):
                data['time_allocation'] = json.dumps(data['time_allocation'])
        
        if 'objectives' in data and data['objectives'] is not None:
            if not isinstance(data['objectives'], str):
                data['objectives'] = json.dumps(data['objectives'])
        
        # Filter data to only include valid columns for Syllabus model
        valid_columns = [c.key for c in Syllabus.__table__.columns]
        update_data = {k: v for k, v in data.items() if k in valid_columns}
        
        # Use transaction for atomic update
        try:
            # Update Header (Note: we use flush=False in repo update typically, 
            # but let's assume we want to control commit here)
            updated_syllabus = self.repository.update(id, update_data)
            sid = updated_syllabus.id
            program_id = updated_syllabus.program_id

            # 1. Update CLOs (Smart In-place Update to preserve IDs for Assessment mappings)
            if clos_data is not None and self.syllabus_clo_repository:
                from infrastructure.models.syllabus_clo_model import SyllabusClo
                # Map existing CLOs for easy lookup
                existing_clos = self.repository.session.query(SyllabusClo).filter_by(syllabus_id=sid).all()
                current_clos_map = {clo.id: clo for clo in existing_clos}
                
                for item in clos_data:
                    clo_id = item.get('id')
                    mappings_data = item.pop('mappings', []) or []
                    raw_plo_mappings = item.pop('plo_mappings_raw', {}) or item.pop('plo_mappings', {}) or item.pop('ploMappings', {})
                    
                    # Process legacy/standardize formats
                    legacy_plo_mappings = {}
                    if isinstance(raw_plo_mappings, list):
                        for m in raw_plo_mappings:
                            if isinstance(m, dict) and ('code' in m or 'ploCode' in m) and 'level' in m:
                                code = m.get('code') or m.get('ploCode')
                                legacy_plo_mappings[code] = m['level']
                    elif isinstance(raw_plo_mappings, dict):
                        legacy_plo_mappings = raw_plo_mappings

                    # Case A: Update Existing or Case B: Create New
                    if clo_id and clo_id in current_clos_map:
                        # Case A: Update Existing
                        existing_clo = current_clos_map.pop(clo_id)
                        for key, value in item.items():
                            if hasattr(existing_clo, key):
                                setattr(existing_clo, key, value)
                        target_clo = existing_clo
                        # Flush to ensure any field changes are sent to DB
                        self.repository.session.flush()
                    else:
                        # Case B: Create New
                        item['syllabus_id'] = sid
                        target_clo = self.syllabus_clo_repository.create(item, commit=False)
                    
                    # FIX: Duplicate Mapping - Delete ALL old mappings before adding new ones
                    if self.clo_plo_mapping_repository:
                        # Delete existing mappings for this CLO
                        from infrastructure.models.clo_plo_mapping_model import CloPloMapping
                        self.repository.session.query(CloPloMapping).filter_by(syllabus_clo_id=target_clo.id).delete()
                        self.repository.session.flush()

                        # Priority 1: Use explicit mappings
                        if mappings_data:
                            for m in mappings_data:
                                if m.get('program_plo_id'):
                                    self.clo_plo_mapping_repository.create({
                                        'syllabus_clo_id': target_clo.id,
                                        'program_plo_id': m.get('program_plo_id'),
                                        'level': m.get('level', 'I')
                                    }, commit=False)
                        
                        # Priority 2: Use legacy/raw mappings
                        elif legacy_plo_mappings and self.program_outcome_repository:
                            from infrastructure.models.program_outcome_model import ProgramOutcome
                            for plo_code, level in legacy_plo_mappings.items():
                                if not level: continue
                                clean_level = str(level).strip().upper()[0] if level else "I"
                                if clean_level not in ('I', 'R', 'M', 'A'):
                                    ai_to_irma = {'H': 'M', 'M': 'R', 'L': 'I'}
                                    clean_level = ai_to_irma.get(clean_level, 'I')
                                
                                plo = self.program_outcome_repository.session.query(ProgramOutcome).filter_by(
                                    program_id=program_id, code=plo_code
                                ).first()
                                if plo:
                                    self.clo_plo_mapping_repository.create({
                                        'syllabus_clo_id': target_clo.id,
                                        'program_plo_id': plo.id,
                                        'level': clean_level
                                    }, commit=False)

                # Process Deletions (Leftovers in map)
                for leftover_id, leftover_clo in current_clos_map.items():
                    self.repository.session.delete(leftover_clo)
                self.repository.session.flush()

            # 2. Update Materials
            if materials_data is not None and self.syllabus_material_repository:
                from infrastructure.models.syllabus_material_model import SyllabusMaterial
                self.repository.session.query(SyllabusMaterial).filter_by(syllabus_id=sid).delete()
                for item in materials_data:
                    item['syllabus_id'] = sid
                    self.syllabus_material_repository.create(item, commit=False)

            # 3. Update Teaching Plans
            if plans_data is not None and self.teaching_plan_repository:
                from infrastructure.models.teaching_plan_model import TeachingPlan
                self.repository.session.query(TeachingPlan).filter_by(syllabus_id=sid).delete()
                for item in plans_data:
                    item['syllabus_id'] = sid
                    self.teaching_plan_repository.create(item, commit=False)

            # 4. Update Assessment Schemes
            if schemes_data is not None and self.assessment_scheme_repository:
                from infrastructure.models.assessment_scheme_model import AssessmentScheme
                existing_schemes = self.repository.session.query(AssessmentScheme).filter_by(syllabus_id=sid).all()
                for scheme_obj in existing_schemes:
                    self.repository.session.delete(scheme_obj)
                self.repository.session.flush()
                
                for scheme in schemes_data:
                    components = scheme.pop('components', [])
                    scheme['syllabus_id'] = sid
                    new_scheme = self.assessment_scheme_repository.create(scheme, commit=False)
                    
                    if self.assessment_component_repository:
                        for comp in components:
                            rubrics = comp.pop('rubrics', [])
                            criteria = comp.pop('criteria', None)
                            clo_ids = comp.pop('clo_ids', [])
                            
                            final_clo_ids = []
                            if isinstance(clo_ids, str):
                                codes = [c.strip() for c in clo_ids.split(',') if c.strip()]
                                for code in codes:
                                    existing_clo = self.repository.session.query(SyllabusClo).filter_by(
                                        syllabus_id=sid, code=code
                                    ).first()
                                    if existing_clo:
                                        final_clo_ids.append(existing_clo.id)
                            elif isinstance(clo_ids, list):
                                for cid in clo_ids:
                                    if isinstance(cid, int):
                                        final_clo_ids.append(cid)
                                    elif isinstance(cid, str):
                                        existing_clo = self.repository.session.query(SyllabusClo).filter_by(
                                            syllabus_id=sid, code=cid
                                        ).first()
                                        if existing_clo:
                                            final_clo_ids.append(existing_clo.id)

                            comp_data = {
                                'name': comp.get('name'),
                                'method': comp.get('method'),
                                'criteria': criteria,
                                'weight': comp.get('weight'),
                                'scheme_id': new_scheme.id
                            }
                            new_comp = self.assessment_component_repository.create(comp_data, commit=False)
                            
                            if criteria and self.rubric_repository:
                                self.rubric_repository.create({
                                    'component_id': new_comp.id,
                                    'criteria': criteria,
                                    'max_score': 10.0
                                }, commit=False)
                            
                            if rubrics and self.rubric_repository:
                                for rub in rubrics:
                                    rub['component_id'] = new_comp.id
                                    self.rubric_repository.create(rub, commit=False)
                                    
                            if final_clo_ids and self.assessment_clo_repository:
                                for clo_id in final_clo_ids:
                                    self.assessment_clo_repository.add_mapping(new_comp.id, clo_id, commit=False)

            # Final Commit for everything
            self.repository.session.commit()
            logger.info(f"Successfully updated syllabus {sid} with all children")
            
            # Re-index
            self._index_to_search(updated_syllabus)
            
            return updated_syllabus

        except Exception as e:
            self.repository.session.rollback()
            logger.error(f"Error updating syllabus: {str(e)}", exc_info=True)
            raise

    def delete_syllabus(self, id: int) -> bool:
        success = self.repository.delete(id)
        if success and self.search_service:
            try:
                self.search_service.delete_index(id)
            except:
                pass
        return success

    # Workflow methods
    def submit_syllabus(self, id: int, user_id: int, user_role: str = None):
        """Submit syllabus for evaluation with comprehensive validation."""
        # BL-001: Use for_update to prevent race condition during submission
        s = self.repository.get_details(id, for_update=True)
        if not s:
            return None
        
        # SEC-002 IDOR: Check ownership
        if user_id and user_role != 'Admin':
            if s.lecturer_id != user_id:
                raise ValueError("Bạn không có quyền gửi duyệt đề cương này (không phải owner).")
        
        current_status = (s.status or '').upper()
        if current_status not in WorkflowStatus.VALID_FOR_SUBMISSION:
            raise ValueError(
                f'Chỉ có thể gửi duyệt ở các trạng thái {WorkflowStatus.VALID_FOR_SUBMISSION}. '
                f'Trạng thái hiện tại: {current_status}'
            )
        
        # Comprehensive Content Validation
        errors = []
        if not s.description or len(s.description.strip()) < 50:
            errors.append('Mô tả học phần phải có ít nhất 50 ký tự.')
        
        if not s.clos or len(s.clos) == 0:
            errors.append('Đề cương phải có ít nhất một Chuẩn đầu ra (CLO).')
        
        if not s.teaching_plans or len(s.teaching_plans) < 5:
            errors.append('Kế hoạch giảng dạy quá ngắn (tối thiểu 5 mục).')

        if not s.materials or len([m for m in s.materials if m.type == 'Main']) == 0:
            errors.append('Thiếu tài liệu học tập chính (Main material).')

        # Validate assessment weight
        if not s.assessment_schemes:
            errors.append('Thiếu ma trận kiểm tra đánh giá.')
        else:
            for scheme in s.assessment_schemes:
                total_weight = sum([float(comp.weight or 0) for comp in (scheme.components or [])])
                if abs(total_weight - 100.0) > 0.1:
                    errors.append(f'Tổng trọng số của "{scheme.name}" phải bằng 100% (hiện tại: {total_weight}%).')
        
        if errors:
            raise ValueError(" | ".join(errors))
        
        from_status = s.status
        updated = self.repository.update(id, {'status': WorkflowStatus.PENDING_REVIEW})
        if self.workflow_log_repository:
            self.workflow_log_repository.create({
                'syllabus_id': id,
                'actor_id': user_id,
                'action': 'SUBMIT',
                'from_status': from_status,
                'to_status': WorkflowStatus.PENDING_REVIEW,
                'comment': 'Đã kiểm tra tính hợp lệ và gửi duyệt.'
            })

        # Track current workflow with deadline (e.g., 7 days for review)
        if self.current_workflow_repository:
            due_date = datetime.now() + timedelta(days=7)
            self.current_workflow_repository.update_or_create(id, {
                'state': WorkflowStatus.PENDING_REVIEW,
                'assigned_user_id': None, # Can be assigned to specific HoD if needed
                'due_date': due_date,
                'last_action_at': datetime.now()
            })
        
        # Notify HoD when a syllabus is submitted
        if self.notification_service:
            self.notification_service.notify_roles(
                roles=['Head of Dept', 'Academic Affairs', 'AA', 'Admin'],
                title='Đề cương mới được gửi',
                message=f'Giảng viên {s.lecturer.full_name if s.lecturer else "N/A"} vừa gửi duyệt môn {s.subject.code if s.subject else "N/A"}.',
                link=f'/syllabus/{id}',
                event_name='syllabus_submitted'
            )
        
        return updated

    def evaluate_syllabus(self, id: int, user_id: int, action: str, comment: Optional[str] = None):
        """Duyệt đề cương đồng bộ 5 bước - Yuri Refactor"""
        logger.info(f"Evaluate: Syllabus {id} by User {user_id}")
        
        # BL-002: Race Condition - Use with_for_update to lock the record
        # FIX: Use get_details with for_update=True
        s = self.repository.get_details(id, for_update=True)
        if not s:
            return None
        
        # Get user role for workflow logic
        user = self.user_repository.get_by_id(user_id) if hasattr(self, 'user_repository') else None
        user_role_names = []
        if user and hasattr(user, 'roles'):
            user_role_names = [ur.role.name for ur in user.roles]
        
        action = action.upper()
        if action not in ('APPROVE', 'REJECT', 'RETURN'):
            raise ValueError(f'Invalid action: {action}. Must be APPROVE, REJECT or RETURN')
        
        current_status = (s.status or WorkflowStatus.DRAFT).upper()
        if current_status not in WorkflowStatus.VALID_FOR_EVALUATION:
             raise ValueError(
                f'Can only evaluate syllabuses in {WorkflowStatus.VALID_FOR_EVALUATION}. Current status: {s.status}'
            )
        
        from_status = s.status
        new_status = from_status

        if action == 'APPROVE':
            # Bước 1: HOD duyệt (Pending Review -> Pending Approval)
            if current_status == WorkflowStatus.PENDING_REVIEW:
                if not any(r in user_role_names for r in ['Head of Dept', 'Admin']):
                    raise ValueError("Chỉ Trưởng bộ môn mới có quyền duyệt ở bước này.")
                new_status = WorkflowStatus.PENDING_APPROVAL
            
            # Bước 2: AA duyệt (Pending Approval -> Approved)
            elif current_status == WorkflowStatus.PENDING_APPROVAL:
                if not any(r in user_role_names for r in ['Academic Affairs', 'AA', 'Admin']):
                    raise ValueError("Chỉ Phòng Đào tạo (AA) mới có quyền duyệt ở bước này.")
                new_status = WorkflowStatus.APPROVED
            
            # Bước 3: Principal duyệt cuối (Approved -> Published)
            elif current_status == WorkflowStatus.APPROVED:
                if not any(r in user_role_names for r in ['Principal', 'Admin']):
                    raise ValueError("Chỉ Hiệu trưởng mới có quyền phê duyệt xuất bản.")
                new_status = WorkflowStatus.PUBLISHED
            else:
                # BL-003: Raise exception instead of silent fallback
                raise ValueError(f"Quyền hạn của bạn không phù hợp để duyệt ở trạng thái {current_status}")
        elif action == 'RETURN':
            if not comment:
                raise ValueError('Comment là bắt buộc khi trả về để sửa chữa.')
            new_status = WorkflowStatus.RETURNED
        else:  # REJECT
            if not comment:
                raise ValueError('Comment là bắt buộc khi từ chối vĩnh viễn.')
            new_status = WorkflowStatus.REJECTED
        
        try:
            # 1. Cập nhật trạng thái trong DB và Commit ngay
            update_data = {'status': new_status}
            if new_status == WorkflowStatus.PUBLISHED:
                update_data['is_active'] = True
                update_data['publish_date'] = datetime.now()
            
            updated = self.repository.update(id, update_data)
            self.repository.session.commit()
            logger.info(f"Sync: Syllabus {id} status updated to {new_status} and committed")
            
            # 2. Ghi log workflow
            if self.workflow_log_repository:
                self.workflow_log_repository.create({
                    'syllabus_id': id,
                    'actor_id': user_id,
                    'action': action,
                    'from_status': from_status,
                    'to_status': new_status,
                    'comment': comment
                })

            # 3. SYNC: Cập nhật Search Engine ngay lập tức với trạng thái mới
            # Refetch to ensure we have the latest state (already committed)
            s_final = self.repository.get_details(id)
            self._index_to_search(s_final)

            # 4. SYNC: Dọn dẹp bảng Current Workflow nếu đã hoàn tất hoặc bị trả về/từ chối
            if self.current_workflow_repository:
                if new_status in (WorkflowStatus.PUBLISHED, WorkflowStatus.RETURNED, WorkflowStatus.REJECTED):
                    try:
                        if hasattr(self.current_workflow_repository, 'delete'):
                            self.current_workflow_repository.delete(id)
                        elif hasattr(self.current_workflow_repository, 'delete_by_syllabus_id'):
                            self.current_workflow_repository.delete_by_syllabus_id(id)
                        logger.info(f"Sync: Workflow record for {id} cleaned up.")
                    except Exception as e:
                        logger.warning(f"Failed to clean up workflow for syllabus {id}: {e}")
                else:
                    # Update bước tiếp theo với deadline từ System Settings (mặc định 5 ngày)
                    deadline_days = 5
                    if self.system_setting_service:
                        deadline_days = self.system_setting_service.get_setting('workflow_deadline_days', 5)
                    
                    due_date = datetime.now() + timedelta(days=deadline_days)
                    self.current_workflow_repository.update_or_create(id, {
                        'state': new_status,
                        'assigned_user_id': None,
                        'due_date': due_date,
                        'last_action_at': datetime.now()
                    })

            # 5. Take Immutable Snapshot if approved/published
            if action == 'APPROVE' and new_status in WorkflowStatus.PUBLIC_STATUSES:
                 if self.snapshot_service:
                     try:
                         # Di chuyển import vào đây để tránh Circular Import
                         from api.schemas.syllabus_schema import SyllabusSchema
                         schema = SyllabusSchema()
                         snapshot_dict = schema.dump(s_final)
                         self.snapshot_service.create_snapshot(
                             syllabus_id=id,
                             version=s_final.version or "1.0",
                             data=snapshot_dict,
                             created_by=user_id
                         )
                         logger.info(f"Snapshot created for syllabus {id} at status {new_status}")
                     except Exception as e:
                         logger.error(f"Failed to create snapshot for syllabus {id}: {str(e)}")

            # 6. Thông báo cho Giảng viên
            if s.lecturer_id and self.notification_service:
                action_text = 'duyệt' if action == 'APPROVE' else 'trả lại'
                self.notification_service.send_notification(
                    user_id=s.lecturer_id,
                    title=f'Đề cương được {action_text}',
                    message=f'Môn {s.subject.code if s.subject else "N/A"} đã được {action_text}. Trạng thái mới: {new_status}',
                    link=f'/syllabus/{id}',
                    event_name='syllabus_evaluated'
                )
            
            # 7. Thông báo cho SV nếu đã Publish
            if new_status == WorkflowStatus.PUBLISHED and self.student_subscription_repository and self.notification_service:
                from infrastructure.models.student_subscription_model import StudentSubscription
                subs = self.student_subscription_repository.session.query(StudentSubscription).filter_by(subject_id=s.subject_id).all()
                for sub in subs:
                    self.notification_service.send_notification(
                        user_id=sub.student_id,
                        title='Cập nhật đề cương môn học',
                        message=f'Đề cương môn {s.subject.code if s.subject else "N/A"} đã được xuất bản phiên bản mới.',
                        link=f'/syllabus/{id}',
                        event_name='syllabus_published',
                        send_email=True
                    )
            
            return updated
            
        except Exception as e:
            self.repository.session.rollback()
            logger.error(f"Critical Error in evaluate_syllabus: {str(e)}")
            raise e

    def get_workflow_logs(self, syllabus_id: int):
        if not self.workflow_log_repository:
            return []
        return self.workflow_log_repository.get_by_syllabus_id(syllabus_id)