from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.teaching_plan_service import TeachingPlanService
from api.schemas.teaching_plan_schema import TeachingPlanSchema

teaching_plan_bp = Blueprint('teaching_plan', __name__, url_prefix='/teaching-plans')

schema = TeachingPlanSchema()

@teaching_plan_bp.route('/syllabus/<int:syllabus_id>', methods=['GET'])
@inject
def list_plans(syllabus_id: int, teaching_plan_service: TeachingPlanService = Provide[Container.teaching_plan_service]):
    """
    List teaching plans for a syllabus
    ---
    tags:
      - Teaching Plans
    parameters:
      - name: syllabus_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of teaching plans
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/TeachingPlan'
    """
    items = teaching_plan_service.list_plans_for_syllabus(syllabus_id)
    return jsonify(schema.dump(items, many=True)), 200

@teaching_plan_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_plan(teaching_plan_service: TeachingPlanService = Provide[Container.teaching_plan_service]):
    """
    Create a teaching plan
    ---
    tags:
      - Teaching Plans
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TeachingPlan'
    responses:
      201:
        description: Teaching plan created
      400:
        description: Validation or creation error
    """
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = teaching_plan_service.create_teaching_plan(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(schema.dump(item)), 201

@teaching_plan_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_plan(id: int, teaching_plan_service: TeachingPlanService = Provide[Container.teaching_plan_service]):
    """
    Update a teaching plan
    ---
    tags:
      - Teaching Plans
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
            $ref: '#/components/schemas/TeachingPlan'
    responses:
      200:
        description: Teaching plan updated
      400:
        description: Validation error
      404:
        description: Teaching plan not found
    """
    data = request.get_json() or {}
    errors = schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400
    item = teaching_plan_service.update_teaching_plan(id, data)
    if not item:
        return jsonify({'message': 'Teaching plan not found'}), 404
    return jsonify(schema.dump(item)), 200

@teaching_plan_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_plan(id: int, teaching_plan_service: TeachingPlanService = Provide[Container.teaching_plan_service]):
    """
    Delete a teaching plan
    ---
    tags:
      - Teaching Plans
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
        description: Teaching plan not found
    """
    ok = teaching_plan_service.delete_teaching_plan(id)
    if not ok:
        return jsonify({'message': 'Teaching plan not found'}), 404
    return '', 204