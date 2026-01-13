from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.subject_relationship_service import SubjectRelationshipService
from api.schemas.subject_relationship_schema import SubjectRelationshipSchema

subject_rel_bp = Blueprint('subject_relationship', __name__, url_prefix='/subject-relationships')
schema = SubjectRelationshipSchema()

@subject_rel_bp.route('/subject/<int:subject_id>', methods=['GET'])
@inject
def list_relationships(subject_id: int, service: SubjectRelationshipService = Provide[Container.subject_relationship_service]):
    """
    List relationships for a subject
    ---
    tags:
      - Subject Relationships
    parameters:
      - name: subject_id
        in: path
        required: true
        schema: {type: integer}
    responses:
      200: {description: List of relationships}
    """
    items = service.get_relationships(subject_id)
    return jsonify(schema.dump(items, many=True)), 200

@subject_rel_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_relationship(service: SubjectRelationshipService = Provide[Container.subject_relationship_service]):
    """
    Create subject relationship
    ---
    tags:
      - Subject Relationships
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/SubjectRelationship'
    responses:
      201: {description: Created}
    """
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = service.add_relationship(data)
        return jsonify(schema.dump(item)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@subject_rel_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_relationship(id: int, service: SubjectRelationshipService = Provide[Container.subject_relationship_service]):
    """
    Delete relationship
    ---
    tags:
      - Subject Relationships
    responses:
      204: {description: Deleted}
    """
    ok = service.remove_relationship(id)
    if not ok:
        return jsonify({'message': 'Relationship not found'}), 404
    return '', 204