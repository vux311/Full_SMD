from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.student_service import StudentService
from api.schemas.student_schema import StudentSubscriptionSchema, StudentReportSchema
from api.middleware import token_required, role_required

student_bp = Blueprint('student', __name__, url_prefix='/student')
sub_schema = StudentSubscriptionSchema()
rep_schema = StudentReportSchema()

@student_bp.route('/subscribe', methods=['POST', 'OPTIONS'], strict_slashes=False)
@token_required
@role_required(['Student', 'Admin'])
@inject
def subscribe(service: StudentService = Provide[Container.student_service]):
    """
    Student subscribes to a subject
    """
    from flask import g
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401
        
    data = request.get_json() or {}
    subject_id = data.get('subject_id')
    if not subject_id:
        return jsonify({'message': 'subject_id is required'}), 400
        
    item = service.subscribe(user_id, subject_id)
    return jsonify(sub_schema.dump(item)), 201

@student_bp.route('/unsubscribe', methods=['POST', 'OPTIONS'], strict_slashes=False)
@token_required
@role_required(['Student', 'Admin'])
@inject
def unsubscribe(service: StudentService = Provide[Container.student_service]):
    """
    Student unsubscribes from a subject
    """
    from flask import g
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401
        
    data = request.get_json() or {}
    subject_id = data.get('subject_id')
    if not subject_id:
        return jsonify({'message': 'subject_id is required'}), 400
        
    ok = service.unsubscribe(user_id, subject_id)
    if not ok:
        return jsonify({'message': 'Subscription not found'}), 404
    return '', 204

@student_bp.route('/report', methods=['POST', 'OPTIONS'], strict_slashes=False)
@token_required
@role_required(['Student', 'Admin'])
@inject
def report(service: StudentService = Provide[Container.student_service]):
    """
    Student reports an issue with a syllabus
    """
    from flask import g
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401
        
    data = request.get_json() or {}
    sid = data.get('syllabus_id')
    content = data.get('content')
    if not sid or not content:
        return jsonify({'message': 'syllabus_id and content are required'}), 400
        
    item = service.report_syllabus(user_id, sid, content)
    return jsonify(rep_schema.dump(item)), 201

@student_bp.route('/reports', methods=['GET', 'OPTIONS'], strict_slashes=False)
@token_required
@role_required(['Admin', 'Head of Dept', 'Academic Affairs'])
@inject
def list_reports(service: StudentService = Provide[Container.student_service]):
    """
    List all student reports (Admin)
    ---
    tags:
      - Student Features
    responses:
      200:
        description: List of reports
    """
    items = service.list_reports()
    return jsonify(rep_schema.dump(items, many=True)), 200

@student_bp.route('/report/<int:id>/resolve', methods=['POST', 'OPTIONS'], strict_slashes=False)
@token_required
@role_required(['Admin', 'Head of Dept', 'Academic Affairs'])
@inject
def resolve_report(id: int, service: StudentService = Provide[Container.student_service]):
    data = request.get_json() or {}
    status = data.get('status', 'RESOLVED')
    note = data.get('admin_note')
    
    item = service.resolve_report(id, status, note)
    if not item:
        return jsonify({'message': 'Report not found'}), 404
        
    return jsonify(rep_schema.dump(item)), 200
