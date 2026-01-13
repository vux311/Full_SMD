from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.rubric_service import RubricService
from api.schemas.rubric_schema import RubricSchema

rubric_bp = Blueprint('rubric', __name__, url_prefix='/rubrics')

schema = RubricSchema()

@rubric_bp.route('/component/<int:component_id>', methods=['GET'])
@inject
def list_rubrics(component_id: int, rubric_service: RubricService = Provide[Container.rubric_service]):
    """
    List rubrics for a component
    ---
    tags:
      - Rubrics
    parameters:
      - name: component_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of rubrics
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Rubric'
    """
    items = rubric_service.list_rubrics_for_component(component_id)
    return jsonify(schema.dump(items, many=True)), 200

@rubric_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_rubric(rubric_service: RubricService = Provide[Container.rubric_service]):
    """
    Create a rubric
    ---
    tags:
      - Rubrics
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Rubric'
    responses:
      201:
        description: Rubric created
      400:
        description: Validation or creation error
    """
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = rubric_service.create_rubric(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(schema.dump(item)), 201

@rubric_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_rubric(id: int, rubric_service: RubricService = Provide[Container.rubric_service]):
    """
    Update a rubric
    ---
    tags:
      - Rubrics
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
            $ref: '#/components/schemas/Rubric'
    responses:
      200:
        description: Rubric updated
      400:
        description: Validation error
      404:
        description: Rubric not found
    """
    data = request.get_json() or {}
    errors = schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400
    item = rubric_service.update_rubric(id, data)
    if not item:
        return jsonify({'message': 'Rubric not found'}), 404
    return jsonify(schema.dump(item)), 200

@rubric_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_rubric(id: int, rubric_service: RubricService = Provide[Container.rubric_service]):
    """
    Delete a rubric
    ---
    tags:
      - Rubrics
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
        description: Rubric not found
    """
    ok = rubric_service.delete_rubric(id)
    if not ok:
        return jsonify({'message': 'Rubric not found'}), 404
    return '', 204