from flask import Blueprint, request, jsonify, g
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.department_service import DepartmentService
from services.system_auditlog_service import SystemAuditLogService
from api.schemas.department_schema import DepartmentSchema
from api.middleware import token_required, role_required

department_bp = Blueprint('department', __name__, url_prefix='/departments')

schema = DepartmentSchema()

@department_bp.route('/', methods=['GET'], strict_slashes=False)
@inject
def list_departments(department_service: DepartmentService = Provide[Container.department_service]):
    """Get all departments
    ---
    get:
      summary: Get all departments
      tags:
        - Departments
      responses:
        200:
          description: List of departments
    """
    departments = department_service.list_departments()
    return jsonify(schema.dump(departments, many=True)), 200

@department_bp.route('/<int:id>', methods=['GET'], strict_slashes=False)
@inject
def get_department(id: int, department_service: DepartmentService = Provide[Container.department_service]):
    """Get department by id
    ---
    get:
      summary: Get department by ID
      tags:
        - Departments
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Department object
        404:
          description: Not found
    """
    department = department_service.get_department(id)
    if not department:
        return jsonify({'message': 'Department not found'}), 404
    return jsonify(schema.dump(department)), 200

@department_bp.route('/', methods=['POST'], strict_slashes=False)
@token_required
@role_required(['Admin', 'Academic Affairs'])
@inject
def create_department(department_service: DepartmentService = Provide[Container.department_service],
                      audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Create a new department
    ---
    post:
      summary: Create a new department
      tags:
        - Departments
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Department'
      responses:
        201:
          description: Department created
        400:
          description: Invalid input
    """
    data = request.get_json() or {}
    try:
        loaded_data = schema.load(data)
    except Exception as e:
        return jsonify(getattr(e, 'messages', str(e))), 400
    department = department_service.create_department(loaded_data)
    
    # Audit log
    try:
        audit_service.create_log(
            user_id=getattr(g, 'user_id', None),
            action_type='CREATE',
            resource_target='Department',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Created department: {department.name} ({department.code})"
        )
    except Exception as ae:
        print(f"Audit log failed: {ae}")

    return jsonify(schema.dump(department)), 201

@department_bp.route('/<int:id>', methods=['PUT'], strict_slashes=False)
@token_required
@role_required(['Admin', 'Academic Affairs'])
@inject
def update_department(id: int, department_service: DepartmentService = Provide[Container.department_service],
                      audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Update an existing department
    ---
    put:
      summary: Update department
      tags:
        - Departments
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
              $ref: '#/components/schemas/Department'
      responses:
        200:
          description: Department updated
        400:
          description: Invalid input
        404:
          description: Department not found
    """
    data = request.get_json() or {}
    try:
        loaded_data = schema.load(data, partial=True)
    except Exception as e:
        return jsonify(getattr(e, 'messages', str(e))), 400
    
    department = department_service.update_department(id, loaded_data)
    if not department:
        return jsonify({'message': 'Department not found'}), 404
    
    # Audit log
    try:
        audit_service.create_log(
            user_id=getattr(g, 'user_id', None),
            action_type='UPDATE',
            resource_target='Department',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Updated department #{id}: {department.code}"
        )
    except Exception as ae:
        print(f"Audit log failed: {ae}")

    return jsonify(schema.dump(department)), 200

@department_bp.route('/<int:id>', methods=['DELETE'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def delete_department(id: int, department_service: DepartmentService = Provide[Container.department_service],
                      audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Delete department
    ---
    delete:
      summary: Delete department
      tags:
        - Departments
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
          description: Department not found
    """
    ok = department_service.delete_department(id)
    if not ok:
        return jsonify({'message': 'Department not found'}), 404
    
    # Audit log
    try:
        audit_service.create_log(
            user_id=getattr(g, 'user_id', None),
            action_type='DELETE',
            resource_target='Department',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Deleted department #{id}"
        )
    except Exception as ae:
        print(f"Audit log failed: {ae}")

    return '', 204
    return '', 204