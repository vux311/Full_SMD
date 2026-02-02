from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.syllabus_service import SyllabusService
from services.ai_service import AiService
from services.syllabus_snapshot_service import SyllabusSnapshotService
from api.schemas.syllabus_schema import SyllabusSchema, SyllabusListSchema
from api.schemas.syllabus_detail_schema import SyllabusDetailSchema
from api.middleware import token_required, role_required
from utils.pagination import get_pagination_params, Pagination
from utils.performance import log_api_request

syllabus_bp = Blueprint('syllabus', __name__, url_prefix='/syllabuses')

schema = SyllabusSchema()
list_schema = SyllabusListSchema()
detail_schema = SyllabusDetailSchema()

@syllabus_bp.route('/check-deadlines', methods=['POST'])
@inject
@role_required('Admin') # Only admin can trigger global deadline check for now
def check_deadlines(syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """Check all active workflows for overdue deadlines
    ---
    post:
      summary: Check for overdue syllabus reviews
      tags:
        - Syllabuses
      responses:
        200:
          description: Number of notifications sent
    """
    notification_count = syllabus_service.check_workflow_deadlines()
    return jsonify({
        "status": "success",
        "notifications_sent": notification_count
    })

@syllabus_bp.route('/', methods=['GET'], strict_slashes=False)
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
    
    # Extract filters
    filters = {}
    if 'status' in request.args:
        filters['status'] = request.args.get('status')

    # Check if pagination requested
    if 'page' in request.args or 'page_size' in request.args:
        items, total = syllabus_service.list_syllabuses_paginated(page, page_size, filters=filters)
        # Transform data for list view
        transformed_items = []
        for item in items:
            transformed_items.append({
                'id': item.id,
                'subject_code': item.subject.code if item.subject else '',
                'subject_name_vi': item.subject.name_vi if item.subject else '',
                'subject_name_en': item.subject.name_en if item.subject else '',
                'credits': item.subject.credits if item.subject else 0,
                'lecturer': item.lecturer.full_name if item.lecturer else '',
                'status': item.status,
                'version': item.version,
                'date_edited': item.updated_at
            })
        pagination = Pagination(list_schema.dump(transformed_items, many=True), page, page_size, total)
        return jsonify(pagination.to_dict()), 200
    else:
        # Legacy support: return all items (apply filters if any)
        items = syllabus_service.list_syllabuses(filters=filters)
        transformed_items = []
        for item in items:
            transformed_items.append({
                'id': item.id,
                'subject_code': item.subject.code if item.subject else '',
                'subject_name_vi': item.subject.name_vi if item.subject else '',
                'subject_name_en': item.subject.name_en if item.subject else '',
                'credits': item.subject.credits if item.subject else 0,
                'lecturer': item.lecturer.full_name if item.lecturer else '',
                'status': item.status,
                'version': item.version,
                'date_edited': item.updated_at
            })
        # Wrap in 'data' key for frontend consistency
        return jsonify({
            'data': list_schema.dump(transformed_items, many=True),
            'total': len(transformed_items)
        }), 200

@syllabus_bp.route('/<int:id>', methods=['GET'], strict_slashes=False)
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


@syllabus_bp.route('/<int:id>/details', methods=['GET'], strict_slashes=False)
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
def compare_syllabuses(syllabus_service: SyllabusService = Provide[Container.syllabus_service], ai_service: AiService = Provide[Container.ai_service]):
    """Compare two syllabuses by id with AI Change Detection
    ---
    get:
      summary: Compare two syllabuses
      tags:
        - Syllabuses
    """
    try:
        base_id = int(request.args.get('baseId') or request.args.get('base_id'))
        target_id = int(request.args.get('targetId') or request.args.get('target_id'))
    except Exception:
        return jsonify({'message': 'base_id and target_id are required integers'}), 400

    base = syllabus_service.get_syllabus_details(base_id)
    target = syllabus_service.get_syllabus_details(target_id)

    if not base or not target:
        return jsonify({'message': 'One or both syllabuses not found'}), 404

    # Basic Comparison
    fields = ['subject_name_vi', 'credits', 'description', 'student_duties', 'course_type', 'component_type']
    diffs = []
    for f in fields:
        base_val = getattr(base, f, None)
        target_val = getattr(target, f, None)
        if base_val != target_val:
            diffs.append({
                'field': f, 
                'old_value': str(base_val or 'N/A'), 
                'new_value': str(target_val or 'N/A'),
                'type': 'Modified'
            })

    # AI Analysis (if requested or by default)
    # We pass serialized versions of both syllabuses to AI
    base_dict = schema.dump(base)
    target_dict = schema.dump(target)
    
    ai_report = ai_service.compare_syllabuses(base_dict, target_dict)

    return jsonify({
        'base_version': base.version or '1.0',
        'target_version': target.version or '2.0',
        'diffs': diffs,
        'ai_report': ai_report
    }), 200


@syllabus_bp.route('/<int:id>/submit', methods=['POST'], strict_slashes=False)
@token_required
@role_required(['Lecturer', 'Admin'])
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
    user_role = getattr(g, 'role', None)
    
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401
    
    try:
        s = syllabus_service.submit_syllabus(id, user_id, user_role)
    except ValueError as e:
        return jsonify({'message': str(e)}), 422
    except Exception as e:
        return jsonify({'message': f'Error submitting syllabus: {str(e)}'}), 500
    
    if not s:
        return jsonify({'message': 'Syllabus not found'}), 404
    
    return jsonify({'message': 'Syllabus submitted successfully', 'data': schema.dump(s)}), 200


@syllabus_bp.route('/<int:id>/evaluate', methods=['POST'], strict_slashes=False)
@token_required
@role_required(['Head of Dept', 'Academic Affairs', 'Principal', 'Admin'])
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

@syllabus_bp.route('/', methods=['POST'], strict_slashes=False)
@token_required
@role_required(['Lecturer', 'Admin'])
@inject
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
    from marshmallow import ValidationError
    raw_data = request.get_json() or {}
    try:
        # Load data using schema to handle transformation and filtering
        data = schema.load(raw_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
        
    try:
        s = syllabus_service.create_syllabus(data)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': f'Error creating syllabus: {str(e)}'}), 400
    return jsonify(schema.dump(s)), 201

@syllabus_bp.route('/<int:id>', methods=['PUT', 'PATCH'], strict_slashes=False)
@token_required
@role_required(['Lecturer', 'Admin'])
@inject
def update_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    from marshmallow import ValidationError
    from flask import g
    user_id = getattr(g, 'user_id', None)
    user_role = getattr(g, 'role', None)
    
    raw_data = request.get_json() or {}
    try:
        # load(partial=True) handles PATCH correctly by only validating provided fields
        data = schema.load(raw_data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
        
    try:
        s = syllabus_service.update_syllabus(id, data, user_id, user_role)
    except ValueError as e:
        return jsonify({'message': str(e)}), 422
    except Exception as e:
        return jsonify({'message': f'Error updating syllabus: {str(e)}'}), 500
        
    if not s:
        return jsonify({'message': 'Syllabus not found'}), 404
    return jsonify(schema.dump(s)), 200

@syllabus_bp.route('/<int:id>', methods=['DELETE'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def delete_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    ok = syllabus_service.delete_syllabus(id)
    if not ok:
        return jsonify({'message': 'Syllabus not found'}), 404
    return '', 204

@syllabus_bp.route('/<int:id>/history', methods=['GET'], strict_slashes=False)
@inject
@token_required
def get_syllabus_history(id: int, current_user, snapshot_service: SyllabusSnapshotService = Provide[Container.syllabus_snapshot_service]):
    """Get history of snapshots for a syllabus"""
    history = snapshot_service.get_syllabus_history(id)
    return jsonify([{
        'id': s.id,
        'version': s.version,
        'created_at': s.created_at.isoformat(),
        'created_by': s.creator.full_name if s.creator else "System"
    } for s in history])

@syllabus_bp.route('/compare-versions', methods=['GET'])
@inject
@token_required
def compare_versions(current_user, snapshot_service: SyllabusSnapshotService = Provide[Container.syllabus_snapshot_service]):
    """Compare two snapshots or a snapshot with current version"""
    s1_id = request.args.get('s1', type=int)
    s2_id_raw = request.args.get('s2')
    syllabus_id = request.args.get('syllabus_id', type=int)

    if not s1_id or not s2_id_raw:
        return jsonify({'message': 'Missing comparison IDs'}), 400

    try:
        if s2_id_raw == 'current':
            if not syllabus_id:
                return jsonify({'message': 'syllabus_id required for current comparison'}), 400
            diff = snapshot_service.compare_with_current(s1_id, syllabus_id)
        else:
            diff = snapshot_service.compare_snapshots(s1_id, int(s2_id_raw))
        return jsonify(diff)
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@syllabus_bp.route('/snapshots/<int:snapshot_id>', methods=['GET'], strict_slashes=False)
@inject
@token_required
def get_snapshot_details(snapshot_id: int, current_user, snapshot_service: SyllabusSnapshotService = Provide[Container.syllabus_snapshot_service]):
    """Get full data of a specific snapshot"""
    snapshot = snapshot_service.get_snapshot(snapshot_id)
    if not snapshot:
        return jsonify({'message': 'Snapshot not found'}), 404
    return jsonify(snapshot.snapshot_data)