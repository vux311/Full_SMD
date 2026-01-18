from flask import Blueprint, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.syllabus_service import SyllabusService
from services.user_service import UserService
from services.analysis_service import AnalysisService
from domain.constants import WorkflowStatus

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/stats')

@dashboard_bp.route('/impact-analysis/<int:syllabus_id>', methods=['GET'])
@inject
def impact_analysis(syllabus_id: int, analysis_service: AnalysisService = Provide[Container.analysis_service]):
    """Analyze impact of changing a syllabus"""
    result = analysis_service.get_impact_analysis(syllabus_id)
    if not result:
        return jsonify({"message": "Syllabus not found"}), 404
    return jsonify(result), 200

@dashboard_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def get_stats(syllabus_service: SyllabusService = Provide[Container.syllabus_service], user_service: UserService = Provide[Container.user_service]):
    syllabuses = syllabus_service.list_syllabuses() or []
    users = user_service.list_users() or []

    total_syllabuses = len(syllabuses)
    total_users = len(users)

    # Group by status using WorkflowStatus constants
    stats_by_status = {
        WorkflowStatus.PUBLISHED: 0,
        WorkflowStatus.APPROVED: 0,
        'Pending': 0,
        WorkflowStatus.DRAFT: 0,
        WorkflowStatus.RETURNED: 0
    }
    for s in syllabuses:
        status_raw = getattr(s, 'status', None) or getattr(s, 'state', None) or WorkflowStatus.DRAFT
        status = status_raw.upper()
        # Normalize
        if status == WorkflowStatus.PUBLISHED:
            stats_by_status[WorkflowStatus.PUBLISHED] += 1
        elif status == WorkflowStatus.APPROVED:
            stats_by_status[WorkflowStatus.APPROVED] += 1
        elif 'PENDING' in status:
            stats_by_status['Pending'] += 1
        elif status in (WorkflowStatus.RETURNED, WorkflowStatus.REJECTED):
            stats_by_status[WorkflowStatus.RETURNED] += 1
        else:
            stats_by_status[WorkflowStatus.DRAFT] += 1

    # Convert to array format for frontend charts
    status_breakdown = [
        {"name": "Đã xuất bản", "value": stats_by_status[WorkflowStatus.PUBLISHED] + stats_by_status[WorkflowStatus.APPROVED], "fill": "#10b981"},
        {"name": "Chờ duyệt", "value": stats_by_status['Pending'], "fill": "#f59e0b"},
        {"name": "Nháp", "value": stats_by_status[WorkflowStatus.DRAFT], "fill": "#6b7280"},
        {"name": "Trả lại", "value": stats_by_status[WorkflowStatus.RETURNED], "fill": "#ef4444"}
    ]

    # Get operational KPIs
    kpis = syllabus_service.get_kpis()

    return jsonify({
        'total_syllabuses': total_syllabuses,
        'total_syllabus': total_syllabuses,  # Alias for frontend
        'total_users': total_users,
        'by_status': stats_by_status,  # Keep for backward compatibility
        'status_breakdown': status_breakdown,  # Array format for charts
        'kpis': kpis
    }), 200

@dashboard_bp.route('/kpis', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def get_kpis(syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """Strategic KPIs for Principal/Admin"""
    try:
        kpis = syllabus_service.get_kpis()
        return jsonify(kpis), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
