from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.syllabus_material_service import SyllabusMaterialService
from api.schemas.syllabus_material_schema import SyllabusMaterialSchema

syllabus_material_bp = Blueprint('syllabus_material', __name__, url_prefix='/syllabus-materials')

schema = SyllabusMaterialSchema()

@syllabus_material_bp.route('/syllabus/<int:syllabus_id>', methods=['GET'])
@inject
def list_materials(syllabus_id: int, syllabus_material_service: SyllabusMaterialService = Provide[Container.syllabus_material_service]):
    """
    List materials for a syllabus
    ---
    tags:
      - Syllabus Materials
    parameters:
      - name: syllabus_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of materials
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/SyllabusMaterial'
    """
    items = syllabus_material_service.get_by_syllabus(syllabus_id)
    return jsonify(schema.dump(items, many=True)), 200

@syllabus_material_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_material(syllabus_material_service: SyllabusMaterialService = Provide[Container.syllabus_material_service]):
    """
    Create a syllabus material
    ---
    tags:
      - Syllabus Materials
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/SyllabusMaterial'
    responses:
      201:
        description: Material created
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
        item = syllabus_material_service.create_material(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(schema.dump(item)), 201

@syllabus_material_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_material(id: int, syllabus_material_service: SyllabusMaterialService = Provide[Container.syllabus_material_service]):
    """
    Delete a syllabus material
    ---
    tags:
      - Syllabus Materials
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
        description: Material not found
    """
    ok = syllabus_material_service.delete_material(id)
    if not ok:
        return jsonify({'message': 'Material not found'}), 404
    return '', 204