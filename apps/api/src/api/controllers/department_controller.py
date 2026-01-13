from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.department_service import DepartmentService
from api.schemas.department_schema import DepartmentSchema

department_bp = Blueprint('department', __name__, url_prefix='/departments')

schema = DepartmentSchema()

@department_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
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

@department_bp.route('/<int:id>', methods=['GET', 'OPTIONS'], strict_slashes=False)
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

@department_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_department(department_service: DepartmentService = Provide[Container.department_service]):
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
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    department = department_service.create_department(data)
    return jsonify(schema.dump(department)), 201

@department_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_department(id: int, department_service: DepartmentService = Provide[Container.department_service]):
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
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    department = department_service.update_department(id, data)
    if not department:
        return jsonify({'message': 'Department not found'}), 404
    return jsonify(schema.dump(department)), 200

@department_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_department(id: int, department_service: DepartmentService = Provide[Container.department_service]):
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
    return '', 204