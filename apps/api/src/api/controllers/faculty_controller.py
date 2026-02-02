from flask import Blueprint, request, jsonify, g
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.faculty_service import FacultyService
from services.system_auditlog_service import SystemAuditLogService
from api.schemas.faculty_schema import FacultySchema
from api.middleware import token_required, role_required

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculties')

schema = FacultySchema()

@faculty_bp.route('/', methods=['GET'], strict_slashes=False)
@inject
def list_faculties(faculty_service: FacultyService = Provide[Container.faculty_service]):
    """Get all faculties
    ---
    get:
      summary: Get all faculties
      tags:
        - Faculties
      responses:
        200:
          description: List of faculties
    """
    faculties = faculty_service.list_faculties()
    return jsonify(schema.dump(faculties, many=True)), 200

@faculty_bp.route('/<int:id>', methods=['GET'], strict_slashes=False)
@inject
def get_faculty(id: int, faculty_service: FacultyService = Provide[Container.faculty_service]):
    """Get faculty by id
    ---
    get:
      summary: Get faculty by ID
      tags:
        - Faculties
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Faculty object
        404:
          description: Not found
    """
    faculty = faculty_service.get_faculty(id)
    if not faculty:
        return jsonify({'message': 'Faculty not found'}), 404
    return jsonify(schema.dump(faculty)), 200

@faculty_bp.route('/', methods=['POST'], strict_slashes=False)
@token_required
@role_required(['Admin', 'Academic Affairs'])
@inject
def create_faculty(faculty_service: FacultyService = Provide[Container.faculty_service],
                   audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Create a new faculty
    ---
    post:
      summary: Create a new faculty
      tags:
        - Faculties
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Faculty'
      responses:
        201:
          description: Faculty created
        400:
          description: Invalid input
    """
    data = request.get_json() or {}
    try:
        loaded_data = schema.load(data)
    except Exception as e:
        return jsonify(getattr(e, 'messages', str(e))), 400
    
    faculty = faculty_service.create_faculty(loaded_data)
    
    # Audit log
    try:
        audit_service.create_log(
            user_id=getattr(g, 'user_id', None),
            action_type='CREATE',
            resource_target='Faculty',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Created faculty: {faculty.name} ({faculty.code})"
        )
    except Exception as ae:
        print(f"Audit log failed: {ae}")
        
    return jsonify(schema.dump(faculty)), 201

@faculty_bp.route('/<int:id>', methods=['PUT'], strict_slashes=False)
@token_required
@role_required(['Admin', 'Academic Affairs'])
@inject
def update_faculty(id: int, faculty_service: FacultyService = Provide[Container.faculty_service],
                   audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Update an existing faculty
    ---
    put:
      summary: Update faculty
      tags:
        - Faculties
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Faculty'
      responses:
        200:
          description: Faculty updated
        400:
          description: Invalid input
        404:
          description: Faculty not found
    """
    data = request.get_json() or {}
    try:
        loaded_data = schema.load(data, partial=True)
    except Exception as e:
        return jsonify(getattr(e, 'messages', str(e))), 400
    
    faculty = faculty_service.update_faculty(id, loaded_data)
    if not faculty:
        return jsonify({'message': 'Faculty not found'}), 404
    
    # Audit log
    try:
        audit_service.create_log(
            user_id=getattr(g, 'user_id', None),
            action_type='UPDATE',
            resource_target='Faculty',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Updated faculty #{id}: {faculty.code}"
        )
    except Exception as ae:
        print(f"Audit log failed: {ae}")

    return jsonify(schema.dump(faculty)), 200

@faculty_bp.route('/<int:id>', methods=['DELETE'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def delete_faculty(id: int, faculty_service: FacultyService = Provide[Container.faculty_service],
                   audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Delete faculty
    ---
    delete:
      summary: Delete faculty
      tags:
        - Faculties
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        204:
          description: Deleted
        404:
          description: Faculty not found
    """
    ok = faculty_service.delete_faculty(id)
    if not ok:
        return jsonify({'message': 'Faculty not found'}), 404
    
    # Audit log
    try:
        audit_service.create_log(
            user_id=getattr(g, 'user_id', None),
            action_type='DELETE',
            resource_target='Faculty',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Deleted faculty #{id}"
        )
    except Exception as ae:
        print(f"Audit log failed: {ae}")

    return '', 204
