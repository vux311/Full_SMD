from flask import Blueprint, request, jsonify, g
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.subject_service import SubjectService
from services.system_auditlog_service import SystemAuditLogService
from api.schemas.subject_schema import SubjectSchema
from api.middleware import token_required, role_required

subject_bp = Blueprint('subject', __name__, url_prefix='/subjects')

schema = SubjectSchema()

@subject_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def list_subjects(subject_service: SubjectService = Provide[Container.subject_service]):
    """Get all subjects
    ---
    get:
      summary: Get all subjects
      tags:
        - Subjects
      responses:
        200:
          description: List of subjects
    """
    subjects = subject_service.list_subjects()
    return jsonify(schema.dump(subjects, many=True)), 200

@subject_bp.route('/<int:id>', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def get_subject(id: int, subject_service: SubjectService = Provide[Container.subject_service]):
    """Get subject by id
    ---
    get:
      summary: Get subject by ID
      tags:
        - Subjects
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Subject object
        404:
          description: Not found
    """
    subject = subject_service.get_subject(id)
    if not subject:
        return jsonify({'message': 'Subject not found'}), 404
    return jsonify(schema.dump(subject)), 200

@subject_bp.route('', methods=['POST'], strict_slashes=False)
@token_required
@role_required(['Admin', 'Academic Affairs'])
@inject
def create_subject(subject_service: SubjectService = Provide[Container.subject_service],
                   audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Create a new subject
    ---
    post:
      summary: Create a new subject
      tags:
        - Subjects
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Subject'
      responses:
        201:
          description: Subject created
        400:
          description: Invalid input
    """
    data = request.get_json() or {}
    try:
        loaded_data = schema.load(data)
    except Exception as e:
        return jsonify(getattr(e, 'messages', str(e))), 400
    subject = subject_service.create_subject(loaded_data)
    
    # Audit log
    try:
        audit_service.create_log(
            user_id=getattr(g, 'user_id', None),
            action_type='CREATE',
            resource_target='Subject',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Created subject: {subject.name_vi} ({subject.code})"
        )
    except Exception as ae:
        print(f"Audit log failed: {ae}")
        
    return jsonify(schema.dump(subject)), 201

@subject_bp.route('/<int:id>', methods=['PUT'], strict_slashes=False)
@token_required
@role_required(['Admin', 'Academic Affairs'])
@inject
def update_subject(id: int, subject_service: SubjectService = Provide[Container.subject_service],
                   audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Update an existing subject
    ---
    put:
      summary: Update subject
      tags:
        - Subjects
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
              $ref: '#/components/schemas/Subject'
      responses:
        200:
          description: Subject updated
        400:
          description: Invalid input
        404:
          description: Subject not found
    """
    data = request.get_json() or {}
    try:
        loaded_data = schema.load(data, partial=True)
    except Exception as e:
        return jsonify(getattr(e, 'messages', str(e))), 400
    
    subject = subject_service.update_subject(id, loaded_data)
    if not subject:
        return jsonify({'message': 'Subject not found'}), 404
    
    # Audit log
    try:
        audit_service.create_log(
            user_id=getattr(g, 'user_id', None),
            action_type='UPDATE',
            resource_target='Subject',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Updated subject #{id}: {subject.code}"
        )
    except Exception as ae:
        print(f"Audit log failed: {ae}")

    return jsonify(schema.dump(subject)), 200

@subject_bp.route('/<int:id>', methods=['DELETE'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def delete_subject(id: int, subject_service: SubjectService = Provide[Container.subject_service],
                   audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Delete subject
    ---
    delete:
      summary: Delete subject
      tags:
        - Subjects
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
          description: Subject not found
    """

    ok = subject_service.delete_subject(id)
    if not ok:
        return jsonify({'message': 'Subject not found'}), 404
    
    # Audit log
    try:
        audit_service.create_log(
            user_id=getattr(g, 'user_id', None),
            action_type='DELETE',
            resource_target='Subject',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Deleted subject #{id}"
        )
    except Exception as ae:
        print(f"Audit log failed: {ae}")

    return '', 204
