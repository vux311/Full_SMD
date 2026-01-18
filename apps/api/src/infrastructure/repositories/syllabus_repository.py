from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from infrastructure.databases.mssql import session
from infrastructure.models.syllabus_model import Syllabus
from infrastructure.models.syllabus_clo_model import SyllabusClo
from infrastructure.models.assessment_scheme_model import AssessmentScheme
from infrastructure.models.assessment_component_model import AssessmentComponent
from infrastructure.models.assessment_clo_model import AssessmentClo

class SyllabusRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self, filters: dict = None) -> List[Syllabus]:
        # Eager load related entities to prevent N+1 queries
        query = (self.session.query(Syllabus)
                .options(
                    joinedload(Syllabus.subject),
                    joinedload(Syllabus.program),
                    joinedload(Syllabus.academic_year),
                    joinedload(Syllabus.lecturer)
                ))
        
        if filters:
            if 'status' in filters and filters['status']:
                status_val = filters['status']
                if isinstance(status_val, list):
                    query = query.filter(Syllabus.status.in_(status_val))
                else:
                    query = query.filter(Syllabus.status == status_val)
                
        return query.all()
    
    def get_all_paginated(self, page: int, page_size: int, filters: dict = None):
        """
        Get paginated syllabuses with eager loading
        Returns: (items, total_count)
        """
        query = (self.session.query(Syllabus)
                .options(
                    joinedload(Syllabus.subject),
                    joinedload(Syllabus.program),
                    joinedload(Syllabus.academic_year),
                    joinedload(Syllabus.lecturer)
                ))
        
        if filters:
            if 'status' in filters and filters['status']:
                status_val = filters['status']
                if isinstance(status_val, list):
                    query = query.filter(Syllabus.status.in_(status_val))
                else:
                    query = query.filter(Syllabus.status == status_val)

        query = query.order_by(Syllabus.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        
        return items, total

    def get_by_id(self, id: int) -> Optional[Syllabus]:
        return (self.session.query(Syllabus)
                .options(
                    joinedload(Syllabus.subject),
                    joinedload(Syllabus.program),
                    joinedload(Syllabus.academic_year),
                    joinedload(Syllabus.lecturer)
                )
                .filter_by(id=id)
                .first())

    def get_by_subject_id(self, subject_id: int) -> List[Syllabus]:
        return (self.session.query(Syllabus)
                .options(
                    joinedload(Syllabus.subject),
                    joinedload(Syllabus.program),
                    joinedload(Syllabus.academic_year),
                    joinedload(Syllabus.lecturer)
                )
                .filter_by(subject_id=subject_id)
                .all())

    def get_active_by_subject(self, subject_id: int) -> Optional[Syllabus]:
        """Get the published or most recent active syllabus for a subject"""
        return (self.session.query(Syllabus)
                .filter(Syllabus.subject_id == subject_id)
                .filter(Syllabus.status.in_(['PUBLISHED', 'APPROVED']))
                .order_by(Syllabus.created_at.desc())
                .first())

    def get_details(self, id: int) -> Optional[Syllabus]:
        # Eagerly load related metadata AND collections
        return (
            self.session.query(Syllabus)
            .options(
                joinedload(Syllabus.subject),
                joinedload(Syllabus.program),
                joinedload(Syllabus.academic_year),
                joinedload(Syllabus.lecturer),
                joinedload(Syllabus.clos).joinedload(SyllabusClo.plo_mappings),
                joinedload(Syllabus.materials),
                joinedload(Syllabus.teaching_plans),
                joinedload(Syllabus.assessment_schemes)
                    .joinedload(AssessmentScheme.components)
                    .options(
                        joinedload(AssessmentComponent.rubrics),
                        joinedload(AssessmentComponent.clos).joinedload(AssessmentClo.syllabus_clo)
                    ),
            )
            .filter_by(id=id)
            .first()
        )

    def create(self, data: dict) -> Syllabus:
        s = Syllabus(**data)
        self.session.add(s)
        self.session.commit()
        self.session.refresh(s)
        return s

    def update(self, id: int, data: dict) -> Optional[Syllabus]:
        s = self.get_by_id(id)
        if not s:
            return None
        for key, value in data.items():
            if hasattr(s, key):
                setattr(s, key, value)
        self.session.commit()
        self.session.refresh(s)
        return s

    def delete(self, id: int) -> bool:
        s = self.get_by_id(id)
        if not s:
            return False
        self.session.delete(s)
        self.session.commit()
        return True