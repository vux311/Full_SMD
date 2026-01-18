from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.system_auditlog_service import SystemAuditLogService
from api.schemas.system_auditlog_schema import SystemAuditLogSchema
from api.middleware import token_required, role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
schema = SystemAuditLogSchema()

@admin_bp.route('/logs', methods=['GET', 'OPTIONS'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def list_logs(service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Get system audit logs
    ---
    get:
      summary: Get system audit logs (Admin only)
      tags:
        - Admin
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
          description: Maximum number of logs to return
      responses:
        200:
          description: List of audit logs
    """
    # Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response, 200
    
    # Get query parameters
    limit = request.args.get('limit', default=50, type=int)
    
    # Fetch logs
    logs = service.list_logs(limit)
    return jsonify(schema.dump(logs, many=True)), 200

@admin_bp.route('/search/reindex', methods=['POST', 'OPTIONS'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def reindex_search(search_service = Provide[Container.search_service],
                   syllabus_service = Provide[Container.syllabus_service]):
    """Recreate search index and index all published syllabuses"""
    if request.method == 'OPTIONS':
        return '', 204
        
    # 1. Recreate index
    success = search_service.recreate_index()
    if not success:
        return jsonify({'message': 'Failed to recreate search index'}), 500
        
    # 2. Re-index all syllabuses (ideally only published)
    syllabuses = syllabus_service.list_syllabuses()
    count = 0
    for s in syllabuses:
        # Using the private method to index
        syllabus_service._index_to_search(s)
        count += 1
        
    return jsonify({'message': f'Search index recreated and {count} syllabuses indexed'}), 200
