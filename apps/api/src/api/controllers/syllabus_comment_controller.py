from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.syllabus_comment_service import SyllabusCommentService
from api.schemas.syllabus_comment_schema import SyllabusCommentSchema

syllabus_comment_bp = Blueprint('syllabus_comment', __name__, url_prefix='/syllabus-comments')
schema = SyllabusCommentSchema()

@syllabus_comment_bp.route('/syllabus/<int:syllabus_id>', methods=['GET'])
@inject
def list_comments(syllabus_id: int, service: SyllabusCommentService = Provide[Container.syllabus_comment_service]):
    """
    List comments for syllabus
    ---
    tags:
      - Comments
    parameters:
      - name: syllabus_id
        in: path
        required: true
        schema: {type: integer}
    responses:
      200: {description: List of comments}
    """
    items = service.get_comments(syllabus_id)
    return jsonify(schema.dump(items, many=True)), 200

@syllabus_comment_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def add_comment(service: SyllabusCommentService = Provide[Container.syllabus_comment_service]):
    """
    Add a comment
    ---
    tags:
      - Comments
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/SyllabusComment'
    responses:
      201: {description: Created}
    """
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = service.add_comment(data)
        return jsonify(schema.dump(item)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@syllabus_comment_bp.route('/<int:id>/resolve', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def resolve_comment(id: int, service: SyllabusCommentService = Provide[Container.syllabus_comment_service]):
    """
    Mark comment as resolved
    ---
    tags:
      - Comments
    responses:
      200: {description: Resolved}
    """
    item = service.resolve_comment(id)
    if not item:
        return jsonify({'message': 'Comment not found'}), 404
    return jsonify(schema.dump(item)), 200

@syllabus_comment_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_comment(id: int, service: SyllabusCommentService = Provide[Container.syllabus_comment_service]):
    """
    Delete comment
    ---
    tags:
      - Comments
    responses:
      204: {description: Deleted}
    """
    ok = service.delete_comment(id)
    if not ok:
        return jsonify({'message': 'Comment not found'}), 404
    return '', 204