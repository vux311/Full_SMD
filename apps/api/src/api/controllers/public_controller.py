"""
Public API endpoints (no authentication required)
For student portal and public access
"""
from flask import Blueprint, jsonify, request
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.syllabus_service import SyllabusService
from api.schemas.syllabus_schema import SyllabusSchema

public_bp = Blueprint('public', __name__, url_prefix='/public')
schema = SyllabusSchema()

@public_bp.route('/syllabus', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def search_public_syllabuses(syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """
    Public search for syllabuses (no authentication required)
    Only returns approved/published syllabuses
    ---
    tags:
      - Public
    parameters:
      - name: search
        in: query
        type: string
        description: Search keyword
      - name: subject_id
        in: query
        type: integer
        description: Filter by subject ID
      - name: program_id
        in: query
        type: integer
        description: Filter by program ID
    responses:
      200:
        description: List of public syllabuses
    """
    search = request.args.get('search', '').strip()
    subject_id = request.args.get('subject_id', type=int)
    program_id = request.args.get('program_id', type=int)
    
    # Get all syllabuses and filter for approved/active only
    all_syllabuses = syllabus_service.list_syllabuses() or []
    
    # Filter for public access: only approved and active
    public_syllabuses = [
        s for s in all_syllabuses
        if getattr(s, 'is_active', True) and 
           getattr(s, 'status', '').upper() in ('APPROVED', 'PUBLISHED')
    ]
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        public_syllabuses = [
            s for s in public_syllabuses
            if (hasattr(s, 'subject') and s.subject and search_lower in str(s.subject.name_vi or '').lower()) or
               (hasattr(s, 'subject') and s.subject and search_lower in str(s.subject.name_en or '').lower()) or
               (hasattr(s, 'subject') and s.subject and search_lower in str(s.subject.code or '').lower())
        ]
    
    # Apply subject filter
    if subject_id:
        public_syllabuses = [s for s in public_syllabuses if getattr(s, 'subject_id', None) == subject_id]
    
    # Apply program filter
    if program_id:
        public_syllabuses = [s for s in public_syllabuses if getattr(s, 'program_id', None) == program_id]
    
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
    ---
    tags:
      - Public
    parameters:
      - name: id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Syllabus details
      404:
        description: Not found or not public
    """
    syllabus = syllabus_service.get_syllabus(id)
    
    if not syllabus:
        return jsonify({'message': 'Syllabus not found'}), 404
    
    # Check if public
    if not (getattr(syllabus, 'is_active', True) and 
            getattr(syllabus, 'status', '').upper() in ('APPROVED', 'PUBLISHED')):
        return jsonify({'message': 'Syllabus not available'}), 404
    
    return jsonify(schema.dump(syllabus)), 200
