from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.assessment_component_service import AssessmentComponentService
from api.schemas.assessment_component_schema import AssessmentComponentSchema

assessment_component_bp = Blueprint('assessment_component', __name__, url_prefix='/assessment-components')

schema = AssessmentComponentSchema()

@assessment_component_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_component(service: AssessmentComponentService = Provide[Container.assessment_component_service]):
    """
    Create an assessment component
    ---
    tags:
      - Assessments
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/AssessmentComponent'
    responses:
      201:
        description: Component created
      400:
        description: Validation or creation error
    """
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = service.create_component(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(schema.dump(item)), 201

@assessment_component_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_component(id: int, service: AssessmentComponentService = Provide[Container.assessment_component_service]):
    """
    Update an assessment component
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
            $ref: '#/components/schemas/AssessmentComponent'
    responses:
      200:
        description: Component updated
      400:
        description: Validation error
      404:
        description: Component not found
    """
    data = request.get_json() or {}
    errors = schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400
    item = service.update_component(id, data)
    if not item:
        return jsonify({'message': 'Component not found'}), 404
    return jsonify(schema.dump(item)), 200

@assessment_component_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_component(id: int, service: AssessmentComponentService = Provide[Container.assessment_component_service]):
    """
    Delete an assessment component
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
        description: Component not found
    """
    ok = service.delete_component(id)
    if not ok:
        return jsonify({'message': 'Component not found'}), 404
    return '', 204