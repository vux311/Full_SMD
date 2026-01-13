from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.program_outcome_service import ProgramOutcomeService
from api.schemas.program_outcome_schema import ProgramOutcomeSchema

program_outcome_bp = Blueprint('program_outcome', __name__, url_prefix='/program-outcomes')
schema = ProgramOutcomeSchema()

@program_outcome_bp.route('/program/<int:program_id>', methods=['GET'])
@inject
def list_plos(program_id: int, service: ProgramOutcomeService = Provide[Container.program_outcome_service]):
    items = service.list_by_program(program_id)
    return jsonify(schema.dump(items, many=True)), 200

@program_outcome_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_plo(service: ProgramOutcomeService = Provide[Container.program_outcome_service]):
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = service.create_plo(data)
        return jsonify(schema.dump(item)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@program_outcome_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_plo(id: int, service: ProgramOutcomeService = Provide[Container.program_outcome_service]):
    data = request.get_json() or {}
    item = service.update_plo(id, data)
    if not item:
        return jsonify({'message': 'PLO not found'}), 404
    return jsonify(schema.dump(item)), 200

@program_outcome_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_plo(id: int, service: ProgramOutcomeService = Provide[Container.program_outcome_service]):
    ok = service.delete_plo(id)
    if not ok:
        return jsonify({'message': 'PLO not found'}), 404
    return '', 204