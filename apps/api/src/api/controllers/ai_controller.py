from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.ai_service import AiService
import logging
import re
from celery.result import AsyncResult

logger = logging.getLogger(__name__)
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

def to_camel_case(snake_str):
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def convert_keys_to_camel(data):
    """Recursively convert all keys in dict/list from snake_case to camelCase"""
    if isinstance(data, dict):
        return {to_camel_case(k): convert_keys_to_camel(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_camel(item) for item in data]
    else:
        return data

@ai_bp.route('/generate', methods=['POST'], strict_slashes=False)
@inject
def generate(ai_service: AiService = Provide[Container.ai_service]):
    """
    Generate syllabus using AI.
    ---
    tags:
      - AI
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            subject_name:
              type: string
    responses:
      200:
        description: Generated syllabus data
      400:
        description: Invalid input
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json() or {}
        subject_name = data.get('subject_name', '').strip()
        
        if not subject_name:
            return jsonify({'message': 'subject_name is required and cannot be empty'}), 400

        logger.info(f"AI generation request for: {subject_name}")
        
        # Call service with error handling
        try:
            res = ai_service.generate(subject_name)
        except Exception as e:
            logger.error(f"AI service error: {e}", exc_info=True)
            return jsonify({'message': f'AI service error: {str(e)}'}), 500
        
        # Validate response type
        if not isinstance(res, dict):
            logger.error(f"Invalid response type from AI service: {type(res)}")
            return jsonify({'message': 'Invalid response from AI service'}), 500
        
        # Handle error response from AI service
        if res.get('error'):
            error_msg = res.get('error')
            logger.warning(f"AI generation error: {error_msg}")
            return jsonify({'message': error_msg}), 400
        
        # Convert snake_case to camelCase for frontend
        res = convert_keys_to_camel(res)
        
        logger.info(f"AI generation successful for: {subject_name}")
        return jsonify(res), 200
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'message': str(e)}), 422
    except Exception as e:
        logger.error(f"Unexpected error in /ai/generate: {e}", exc_info=True)
        return jsonify({'message': 'Unexpected error occurred'}), 500

@ai_bp.route('/summary/async', methods=['POST'], strict_slashes=False)
@inject
def summary_async(syllabus_service = Provide[Container.syllabus_service]):
    """
    Trigger background task for syllabus summary.
    ---
    tags:
      - AI
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            syllabus_id:
              type: integer
    responses:
      202:
        description: Task started
      404:
        description: Syllabus not found
    """
    from tasks import generate_syllabus_summary_task
    data = request.get_json() or {}
    sid = data.get('syllabus_id')
    if not sid:
        return jsonify({'message': 'syllabus_id is required'}), 400
        
    s = syllabus_service.get_syllabus_details(sid)
    if not s:
        return jsonify({'message': 'Syllabus not found'}), 404
        
    from api.schemas.syllabus_schema import SyllabusSchema
    schema = SyllabusSchema()
    s_data = schema.dump(s)
    
    # Trigger task
    task = generate_syllabus_summary_task.delay(s_data)
    return jsonify({
        'task_id': task.id,
        'status': 'PENDING',
        'message': 'Summary task started in background'
    }), 202

@ai_bp.route('/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Check background task status.
    ---
    tags:
      - AI
    parameters:
      - name: task_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Current task status and result if finished
    """
    res = AsyncResult(task_id)
    if res.ready():
        if res.failed():
            return jsonify({
                'status': 'FAILURE',
                'error': str(res.result)
            })
        return jsonify({
            'status': 'SUCCESS',
            'result': res.result
        })
    return jsonify({'status': res.status})

@ai_bp.route('/summary', methods=['POST'], strict_slashes=False)
@inject
def summary(ai_service: AiService = Provide[Container.ai_service], 
            syllabus_service = Provide[Container.syllabus_service]):
    """
    Summarize syllabus using AI (Synchronous).
    ---
    tags:
      - AI
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            syllabus_id:
              type: integer
    responses:
      200:
        description: Syllabus summary
      404:
        description: Syllabus not found
    """
    data = request.get_json() or {}
    sid = data.get('syllabus_id')
    if not sid:
        return jsonify({'message': 'syllabus_id is required'}), 400
        
    s = syllabus_service.get_syllabus_details(sid)
    if not s:
        return jsonify({'message': 'Syllabus not found'}), 404
        
    from api.schemas.syllabus_schema import SyllabusSchema
    schema = SyllabusSchema()
    s_data = schema.dump(s)
    
    res = ai_service.summarize_syllabus(s_data, sid)
    if 'error' in res:
        return jsonify({'message': res['error']}), 500
        
    return jsonify(res), 200

@ai_bp.route('/analyze-alignment', methods=['POST'], strict_slashes=False)
@inject
def analyze_alignment(ai_service: AiService = Provide[Container.ai_service],
                     syllabus_service = Provide[Container.syllabus_service]):
    """Analyze CLO-PLO alignment using AI"""
    data = request.get_json() or {}
    sid = data.get('syllabus_id')
    if not sid:
        return jsonify({'message': 'syllabus_id is required'}), 400
        
    s = syllabus_service.get_syllabus_details(sid)
    if not s:
        return jsonify({'message': 'Syllabus not found'}), 404
    
    # Prepare data for AI
    clos = [{'code': c.code, 'description': c.description} for c in (s.clos or [])]
    
    # Get PLOs from program
    plos = []
    program = s.program
    if program and hasattr(program, 'outcomes'):
        plos = [{'code': p.code, 'description': p.description} for p in (program.outcomes or [])]
    
    # Get current mappings
    mappings = []
    for c in (s.clos or []):
        if hasattr(c, 'plo_mappings'):
            for m in (c.plo_mappings or []):
                mappings.append({
                    'clo': c.code,
                    'plo': m.program_plo.code if m.program_plo else 'N/A',
                    'level': m.level
                })
            
    res = ai_service.analyze_clo_plo_alignment(clos, plos, mappings)
    if 'error' in res:
        return jsonify({'message': res['error']}), 500
        
    return jsonify(res), 200

@ai_bp.route('/compare', methods=['POST'], strict_slashes=False)
@inject
def compare(ai_service: AiService = Provide[Container.ai_service],
            syllabus_service = Provide[Container.syllabus_service]):
    """
    Compare two syllabus versions using AI.
    ---
    tags:
      - AI
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            base_syllabus_id:
              type: integer
              description: ID of the older/base syllabus
            target_syllabus_id:
              type: integer
              description: ID of the newer/target syllabus
    responses:
      200:
        description: Comparison report
      404:
        description: Syllabus not found
    """
    data = request.get_json() or {}
    base_id = data.get('base_syllabus_id')
    target_id = data.get('target_syllabus_id')

    if not base_id or not target_id:
        return jsonify({'message': 'Both base_syllabus_id and target_syllabus_id are required'}), 400

    base_s = syllabus_service.get_syllabus_details(base_id)
    target_s = syllabus_service.get_syllabus_details(target_id)

    if not base_s:
        return jsonify({'message': f'Base syllabus {base_id} not found'}), 404
    if not target_s:
        return jsonify({'message': f'Target syllabus {target_id} not found'}), 404

    from api.schemas.syllabus_schema import SyllabusSchema
    schema = SyllabusSchema()
    
    base_data = schema.dump(base_s)
    target_data = schema.dump(target_s)

    res = ai_service.compare_syllabuses(base_data, target_data)
    if 'error' in res:
        return jsonify({'message': res['error']}), 500
        
    return jsonify(res), 200
