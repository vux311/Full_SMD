from typing import List
from infrastructure.repositories.assessment_clo_repository import AssessmentCloRepository

class AssessmentCloService:
    def __init__(self, repository: AssessmentCloRepository, component_repository=None, syllabus_clo_repository=None, assessment_scheme_repository=None):
        self.repository = repository
        self.component_repository = component_repository
        self.syllabus_clo_repository = syllabus_clo_repository
        self.assessment_scheme_repository = assessment_scheme_repository

    def get_clos_for_component(self, component_id: int) -> List:
        return self.repository.get_clos_by_component(component_id)

    def add_mapping(self, component_id: int, syllabus_clo_id: int):
        component = self.component_repository.get_by_id(component_id)
        if not component:
            raise ValueError('Invalid component_id')
        syllabus_clo = self.syllabus_clo_repository.get_by_id(syllabus_clo_id)
        if not syllabus_clo:
            raise ValueError('Invalid syllabus_clo_id')

        # Determine the syllabus id for the component (via scheme relationship or scheme repository)
        comp_syllabus_id = None
        if getattr(component, 'scheme', None):
            comp_syllabus_id = component.scheme.syllabus_id
        elif hasattr(component, 'scheme_id'):
            if not self.assessment_scheme_repository:
                raise ValueError('Cannot determine component syllabus without assessment_scheme_repository')
            scheme = self.assessment_scheme_repository.get_by_id(component.scheme_id)
            if not scheme:
                raise ValueError('Invalid component: linked scheme not found')
            comp_syllabus_id = scheme.syllabus_id
        else:
            raise ValueError('Invalid component: cannot resolve related scheme')

        # Ensure both belong to the same syllabus
        if comp_syllabus_id != syllabus_clo.syllabus_id:
            raise ValueError('Cross-reference Error: Component and CLO must belong to the same Syllabus')

        return self.repository.add_mapping(component_id, syllabus_clo_id)

    def remove_mapping(self, component_id: int, syllabus_clo_id: int) -> bool:
        return self.repository.remove_mapping(component_id, syllabus_clo_id)