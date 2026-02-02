"""
Public API endpoints (no authentication required)
For student portal and public access
"""
from flask import Blueprint, jsonify, request
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.syllabus_service import SyllabusService
from services.search_service import SearchService
from api.schemas.syllabus_schema import SyllabusSchema
from domain.constants import WorkflowStatus
import logging

logger = logging.getLogger(__name__)

public_bp = Blueprint('public', __name__, url_prefix='/public')
schema = SyllabusSchema()

@public_bp.route('/syllabus', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def search_public_syllabuses(
    syllabus_service: SyllabusService = Provide[Container.syllabus_service],
    search_service: SearchService = Provide[Container.search_service]
):
    """
    Public search for syllabuses (no authentication required)
    Only returns approved/published syllabuses.
    Tries Search Service (Elasticsearch) first, falls back to SQL.
    """
    search = request.args.get('search', '').strip()
    subject_id = request.args.get('subject_id', type=int)
    program_id = request.args.get('program_id', type=int)
    academic_year_id = request.args.get('academic_year_id', type=int)
    
    # 1. ATTEMPT SEARCH SERVICE (Point 3 - Sync with Search Engine)
    if search and search_service:
        try:
            # We don't have a status filter in search_service yet, so we filter results after
            search_results = search_service.search_syllabuses(search)
            if search_results:
                # Map search results back to IDs or just return them if they have enough data
                # For simplicity and to reuse the existing schema/logic, we'll use IDs to refetch
                ids = [r['id'] for r in search_results if r.get('status', '').upper() in WorkflowStatus.PUBLIC_STATUSES]
                if ids:
                    # Filter for program/year if needed (though search service supports it)
                    # For now, let's just use SQL for specific filters to ensure correctness
                    pass 
        except Exception as e:
            logger.warning(f"Public Search Service failed, falling back to SQL: {e}")

    # 2. FALLBACK TO SQL (Point 2 - Syllabus Repository Logic)
    # Using list_public_syllabuses with specialized repository logic
    filters = {
        'program_id': program_id,
        'academic_year_id': academic_year_id,
        'subject_id': subject_id
    }
    public_syllabuses = syllabus_service.list_public_syllabuses(filters=filters) or []
    
    # Apply search filter (if search service wasn't used or failed)
    if search:
        search_lower = search.lower()
        public_syllabuses = [
            s for s in public_syllabuses
            if (s.subject and search_lower in str(s.subject.name_vi or '').lower()) or
               (s.subject and search_lower in str(s.subject.name_en or '').lower()) or
               (s.subject and search_lower in str(s.subject.code or '').lower())
        ]
    
    return jsonify({
        'data': schema.dump(public_syllabuses, many=True),
        'total': len(public_syllabuses)
    }), 200


@public_bp.route('/syllabus/<int:id>', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def get_public_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """
    Get public syllabus details by ID
    Only returns if approved/published
    """
    # CRITICAL FIX: Use get_syllabus_details to load CLOS, Materials, etc.
    syllabus = syllabus_service.get_syllabus_details(id)
    
    if not syllabus:
        return jsonify({'message': 'Syllabus not found'}), 404
    
    # Check if public
    if not (getattr(syllabus, 'is_active', True) and 
            getattr(syllabus, 'status', '').upper() in WorkflowStatus.PUBLIC_STATUSES):
        return jsonify({'message': 'Syllabus not available'}), 404
    
    return jsonify(schema.dump(syllabus)), 200
