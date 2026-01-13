from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.syllabus_service import SyllabusService
from api.schemas.syllabus_schema import SyllabusSchema
from api.schemas.syllabus_detail_schema import SyllabusDetailSchema
from api.middleware import token_required
from utils.pagination import get_pagination_params, Pagination
from utils.performance import log_api_request

syllabus_bp = Blueprint('syllabus', __name__, url_prefix='/syllabuses')

schema = SyllabusSchema()
detail_schema = SyllabusDetailSchema()

@syllabus_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
@log_api_request
def list_syllabuses(syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """List syllabuses with pagination
    ---
    get:
      summary: List syllabuses (supports pagination)
      tags:
        - Syllabuses
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
      responses:
        200:
          description: Paginated list of syllabuses
    """
    # Get pagination params
    page, page_size, _ = get_pagination_params(default_page_size=20, max_page_size=100)
    
    # Check if pagination requested
    if 'page' in request.args or 'page_size' in request.args:
        items, total = syllabus_service.list_syllabuses_paginated(page, page_size)
        pagination = Pagination(schema.dump(items, many=True), page, page_size, total)
        return jsonify(pagination.to_dict()), 200
    else:
        # Legacy support: return all items
        items = syllabus_service.list_syllabuses()
        return jsonify(schema.dump(items, many=True)), 200

@syllabus_bp.route('/<int:id>', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def get_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """Get syllabus
    ---
    get:
      summary: Get syllabus by id
      tags:
        - Syllabuses
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Syllabus object
        404:
          description: Not found
    """
    s = syllabus_service.get_syllabus(id)
    if not s:
        return jsonify({'message': 'Syllabus not found'}), 404
    return jsonify(schema.dump(s)), 200


@syllabus_bp.route('/<int:id>/details', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def get_syllabus_details(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """Get full syllabus details
    ---
    get:
      summary: Get syllabus details by id
      tags:
        - Syllabuses
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Syllabus detail object
        404:
          description: Not found
    """
    s = syllabus_service.get_syllabus_details(id)
    if not s:
        return jsonify({'message': 'Syllabus not found'}), 404
    return jsonify(detail_schema.dump(s)), 200


@syllabus_bp.route('/compare', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def compare_syllabuses(syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """Compare two syllabuses by id
    ---
    get:
      summary: Compare two syllabuses
      tags:
        - Syllabuses
      parameters:
        - name: base_id
          in: query
          required: true
          schema:
            type: integer
        - name: target_id
          in: query
          required: true
          schema:
            type: integer
    responses:
      200:
        description: Differences between the two syllabuses
      404:
        description: Syllabus not found
    """
    try:
        base_id = int(request.args.get('baseId') or request.args.get('base_id'))
        target_id = int(request.args.get('targetId') or request.args.get('target_id'))
    except Exception:
        return jsonify({'message': 'base_id and target_id query parameters are required and must be integers'}), 400

    base = syllabus_service.get_syllabus_details(base_id)
    target = syllabus_service.get_syllabus_details(target_id)

    if not base or not target:
        return jsonify({'message': 'One or both syllabuses not found'}), 404

    # Fields to compare
    fields = ['subject_name_vi', 'credits', 'description', 'student_duties']
    diffs = []
    for f in fields:
        base_val = getattr(base, f, None)
        target_val = getattr(target, f, None)
        if base_val != target_val:
            diffs.append({'field': f, 'base': base_val, 'target': target_val})

    # Compare CLO counts
    base_clos = getattr(base, 'clos', []) or []
    target_clos = getattr(target, 'clos', []) or []
    if len(base_clos) != len(target_clos):
        diffs.append({'field': 'clos_count', 'base': len(base_clos), 'target': len(target_clos)})

    return jsonify({'diffs': diffs}), 200


@syllabus_bp.route('/<int:id>/submit', methods=['POST', 'OPTIONS'], strict_slashes=False)
@token_required
@inject
def submit_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """Submit a syllabus for evaluation (requires authentication)
    ---
    post:
      summary: Submit syllabus
      tags:
        - Syllabuses
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
      responses:
        200:
          description: Submitted syllabus
        400:
          description: Invalid action
        401:
          description: Unauthorized
        404:
          description: Not found
    """
    from flask import g
    user_id = getattr(g, 'user_id', None)
    
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    try:
        s = syllabus_service.submit_syllabus(id, user_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 422
    except Exception as e:
        return jsonify({'message': f'Error submitting syllabus: {str(e)}'}), 500
    
    if not s:
        return jsonify({'message': 'Syllabus not found'}), 404
    
    return jsonify({'message': 'Syllabus submitted successfully', 'data': schema.dump(s)}), 200


@syllabus_bp.route('/<int:id>/evaluate', methods=['POST', 'OPTIONS'], strict_slashes=False)
@token_required
@inject
def evaluate_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """Evaluate (approve/reject) a syllabus (requires authentication)
    ---
    post:
      summary: Evaluate syllabus
      tags:
        - Syllabuses
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
      responses:
        200:
          description: Evaluation result
        400:
          description: Invalid action or missing comment
        401:
          description: Unauthorized
        404:
          description: Not found
    """
    from flask import g
    user_id = getattr(g, 'user_id', None)
    
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    data = request.get_json() or {}
    action = data.get('action')
    comment = data.get('comment')
    
    if not action:
        return jsonify({'message': 'action is required'}), 422
    
    try:
        s = syllabus_service.evaluate_syllabus(id, user_id, action, comment)
    except ValueError as e:
        return jsonify({'message': str(e)}), 422
    except Exception as e:
        return jsonify({'message': f'Error evaluating syllabus: {str(e)}'}), 500
    
    if not s:
        return jsonify({'message': 'Syllabus not found'}), 404
    
    return jsonify({'message': 'Evaluation completed', 'data': schema.dump(s)}), 200


@syllabus_bp.route('/<int:id>/workflow-logs', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def get_workflow_logs(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """Get workflow logs for a syllabus
    ---
    get:
      summary: Get workflow logs
      tags:
        - Syllabuses
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: List of workflow logs
        404:
          description: Not found
    """
    logs = syllabus_service.get_workflow_logs(id)
    from api.schemas.workflow_log_schema import WorkflowLogSchema
    schema_w = WorkflowLogSchema()
    return jsonify(schema_w.dump(logs, many=True)), 200

@syllabus_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
@token_required
def create_syllabus(syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """Create a syllabus
    ---
    post:
      summary: Create syllabus
      tags:
        - Syllabuses
      requestBody:
        required: true
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        s = syllabus_service.create_syllabus(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(schema.dump(s)), 201

@syllabus_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    data = request.get_json() or {}
    errors = schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400
    s = syllabus_service.update_syllabus(id, data)
    if not s:
        return jsonify({'message': 'Syllabus not found'}), 404
    return jsonify(schema.dump(s)), 200

@syllabus_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    ok = syllabus_service.delete_syllabus(id)
    if not ok:
        return jsonify({'message': 'Syllabus not found'}), 404
    return '', 204