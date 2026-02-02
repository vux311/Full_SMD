from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.program_service import ProgramService
from api.schemas.program_schema import ProgramSchema
from api.middleware import token_required, role_required
from marshmallow import ValidationError

program_bp = Blueprint('program', __name__, url_prefix='/programs')

schema = ProgramSchema()

@program_bp.route('/', methods=['GET'], strict_slashes=False)
@inject
def list_programs(program_service: ProgramService = Provide[Container.program_service]):
    """Get all programs
    ---
    get:
      summary: Get all programs
      tags:
        - Programs
      responses:
        200:
          description: List of programs
    """
    items = program_service.list_programs()
    return jsonify(schema.dump(items, many=True)), 200

@program_bp.route('/', methods=['POST'], strict_slashes=False)
@token_required
@role_required(['Admin', 'Academic Affairs'])
@inject
def create_program(program_service: ProgramService = Provide[Container.program_service]):
    data = request.get_json() or {}
    try:
        loaded_data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 400
    p = program_service.create_program(loaded_data)
    return jsonify(schema.dump(p)), 201

@program_bp.route('/<int:id>', methods=['PUT'], strict_slashes=False)
@inject
def update_program(id: int, program_service: ProgramService = Provide[Container.program_service]):
    data = request.get_json() or {}
    try:
        loaded_data = schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 400
    p = program_service.update_program(id, loaded_data)
    if not p:
        return jsonify({'message': 'Program not found'}), 404
    return jsonify(schema.dump(p)), 200

@program_bp.route('/<int:id>', methods=['DELETE'], strict_slashes=False)
@inject
def delete_program(id: int, program_service: ProgramService = Provide[Container.program_service]):
    ok = program_service.delete_program(id)
    if not ok:
        return jsonify({'message': 'Program not found'}), 404
    return '', 204