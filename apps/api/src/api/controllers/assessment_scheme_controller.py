from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.assessment_scheme_service import AssessmentSchemeService
from api.schemas.assessment_scheme_schema import AssessmentSchemeSchema

assessment_scheme_bp = Blueprint('assessment_scheme', __name__, url_prefix='/assessment-schemes')

schema = AssessmentSchemeSchema()

@assessment_scheme_bp.route('/syllabus/<int:syllabus_id>', methods=['GET'])
@inject
def list_schemes(syllabus_id: int, service: AssessmentSchemeService = Provide[Container.assessment_scheme_service]):
    """
    List assessment schemes for a syllabus
    ---
    tags:
      - Assessments
    parameters:
      - name: syllabus_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of assessment schemes
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/AssessmentScheme'
    """
    items = service.list_schemes_for_syllabus(syllabus_id)
    return jsonify(schema.dump(items, many=True)), 200

@assessment_scheme_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_scheme(service: AssessmentSchemeService = Provide[Container.assessment_scheme_service]):
    """
    Create an assessment scheme
    ---
    tags:
      - Assessments
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/AssessmentScheme'
    responses:
      201:
        description: Scheme created
      400:
        description: Validation or creation error
    """
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = service.create_scheme(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(schema.dump(item)), 201

@assessment_scheme_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_scheme(id: int, service: AssessmentSchemeService = Provide[Container.assessment_scheme_service]):
    """
    Update an assessment scheme
    ---
    tags:
      - Assessments
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
            $ref: '#/components/schemas/AssessmentScheme'
    responses:
      200:
        description: Scheme updated
      400:
        description: Validation error
      404:
        description: Scheme not found
    """
    data = request.get_json() or {}
    errors = schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400
    item = service.update_scheme(id, data)
    if not item:
        return jsonify({'message': 'Scheme not found'}), 404
    return jsonify(schema.dump(item)), 200

@assessment_scheme_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_scheme(id: int, service: AssessmentSchemeService = Provide[Container.assessment_scheme_service]):
    """
    Delete an assessment scheme
    ---
    tags:
      - Assessments
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
        description: Scheme not found
    """
    ok = service.delete_scheme(id)
    if not ok:
        return jsonify({'message': 'Scheme not found'}), 404
    return '', 204