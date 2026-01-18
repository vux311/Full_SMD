from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.syllabus_clo_service import SyllabusCloService
from api.schemas.syllabus_clo_schema import SyllabusCloSchema

syllabus_clo_bp = Blueprint('syllabus_clo', __name__, url_prefix='/syllabus-clos')

schema = SyllabusCloSchema()

@syllabus_clo_bp.route('/syllabus/<int:syllabus_id>', methods=['GET'])
@inject
def list_clos(syllabus_id: int, syllabus_clo_service: SyllabusCloService = Provide[Container.syllabus_clo_service]):
    """
    List CLOs for a syllabus
    ---
    tags:
      - Syllabus CLOs
    parameters:
      - name: syllabus_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of CLOs
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/SyllabusClo'
    """
    items = syllabus_clo_service.get_by_syllabus(syllabus_id)
    return jsonify(schema.dump(items, many=True)), 200

@syllabus_clo_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_clo(syllabus_clo_service: SyllabusCloService = Provide[Container.syllabus_clo_service]):
    """
    Create a new CLO for a syllabus
    ---
    tags:
      - Syllabus CLOs
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/SyllabusClo'
    responses:
      201:
        description: CLO created
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
        item = syllabus_clo_service.create_clo(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(schema.dump(item)), 201

@syllabus_clo_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_clo(id: int, syllabus_clo_service: SyllabusCloService = Provide[Container.syllabus_clo_service]):
    """
    Update an existing CLO
    ---
    tags:
      - Syllabus CLOs
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
            $ref: '#/components/schemas/SyllabusClo'
    responses:
      200:
        description: CLO updated
      400:
        description: Validation error
      404:
        description: CLO not found
    """
    data = request.get_json() or {}
    errors = schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400
    item = syllabus_clo_service.update_clo(id, data)
    if not item:
        return jsonify({'message': 'CLO not found'}), 404
    return jsonify(schema.dump(item)), 200

@syllabus_clo_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_clo(id: int, syllabus_clo_service: SyllabusCloService = Provide[Container.syllabus_clo_service]):
    """
    Delete a CLO by id
    ---
    tags:
      - Syllabus CLOs
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
        description: CLO not found
    """
    ok = syllabus_clo_service.delete_clo(id)
    if not ok:
        return jsonify({'message': 'CLO not found'}), 404
    return '', 204