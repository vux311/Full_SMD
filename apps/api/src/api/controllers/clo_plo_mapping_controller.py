from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.clo_plo_mapping_service import CloPloMappingService
from api.schemas.clo_plo_mapping_schema import CloPloMappingSchema

clo_plo_mapping_bp = Blueprint('clo_plo_mapping', __name__, url_prefix='/clo-plo-mappings')
schema = CloPloMappingSchema()

@clo_plo_mapping_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_mapping(service: CloPloMappingService = Provide[Container.clo_plo_mapping_service]):
    """
    Create CLO-PLO Mapping
    ---
    tags:
      - Mappings (CLO-PLO)
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/CloPloMapping'
    responses:
      201: {description: Created}
      400: {description: Error}
    """
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = service.create_mapping(data)
        return jsonify(schema.dump(item)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@clo_plo_mapping_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_mapping(id: int, service: CloPloMappingService = Provide[Container.clo_plo_mapping_service]):
    """
    Delete CLO-PLO Mapping
    ---
    tags:
      - Mappings (CLO-PLO)
    parameters:
      - name: id
        in: path
        required: true
        schema: {type: integer}
    responses:
      204: {description: Deleted}
    """
    ok = service.delete_mapping(id)
    if not ok:
        return jsonify({'message': 'Mapping not found'}), 404
    return '', 204