from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.ai_service import AiService
import logging

logger = logging.getLogger(__name__)
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/generate', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def generate(ai_service: AiService = Provide[Container.ai_service]):
    """Generate syllabus using AI with comprehensive error handling."""
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
        
        logger.info(f"AI generation successful for: {subject_name}")
        return jsonify(res), 200
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'message': str(e)}), 422
    except Exception as e:
        logger.error(f"Unexpected error in /ai/generate: {e}", exc_info=True)
        return jsonify({'message': 'Unexpected error occurred'}), 500
