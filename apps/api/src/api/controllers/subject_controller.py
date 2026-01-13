from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.subject_service import SubjectService
from api.schemas.subject_schema import SubjectSchema

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

@subject_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_subject(subject_service: SubjectService = Provide[Container.subject_service]):
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
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    subject = subject_service.create_subject(data)
    return jsonify(schema.dump(subject)), 201

@subject_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_subject(id: int, subject_service: SubjectService = Provide[Container.subject_service]):
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
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    subject = subject_service.update_subject(id, data)
    if not subject:
        return jsonify({'message': 'Subject not found'}), 404
    return jsonify(schema.dump(subject)), 200

@subject_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_subject(id: int, subject_service: SubjectService = Provide[Container.subject_service]):
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
    if request.method == 'OPTIONS':
        return '', 200
    ok = subject_service.delete_subject(id)
    if not ok:
        return jsonify({'message': 'Subject not found'}), 404
    return '', 204
