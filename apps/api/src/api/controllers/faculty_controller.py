from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.faculty_service import FacultyService
from api.schemas.faculty_schema import FacultySchema

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculties')

schema = FacultySchema()

@faculty_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
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

@faculty_bp.route('/<int:id>', methods=['GET', 'OPTIONS'], strict_slashes=False)
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

@faculty_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_faculty(faculty_service: FacultyService = Provide[Container.faculty_service]):
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
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    faculty = faculty_service.create_faculty(data)
    return jsonify(schema.dump(faculty)), 201

@faculty_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_faculty(id: int, faculty_service: FacultyService = Provide[Container.faculty_service]):
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
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    faculty = faculty_service.update_faculty(id, data)
    if not faculty:
        return jsonify({'message': 'Faculty not found'}), 404
    return jsonify(schema.dump(faculty)), 200

@faculty_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_faculty(id: int, faculty_service: FacultyService = Provide[Container.faculty_service]):
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
    return '', 204