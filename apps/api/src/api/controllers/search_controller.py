from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.search_service import SearchService
from services.ocr_service import OCRService
import os
import logging

logger = logging.getLogger(__name__)
search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/syllabuses', methods=['GET'])
@inject
def search_syllabuses(search_service: SearchService = Provide[Container.search_service]):
    """
    Search syllabuses using full-text or semantic search.
    ---
    tags:
      - Search
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: The search query text
      - name: type
        in: query
        type: string
        enum: [text, semantic, hybrid]
        default: hybrid
        description: The type of search algorithm to use
      - name: program
        in: query
        type: string
        description: Filter by Program Name (Major)
      - name: academic_year
        in: query
        type: string
        description: Filter by Academic Year Code
    responses:
      200:
        description: List of search results
    """
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'hybrid')
    filters = {
        'program': request.args.get('program'),
        'academic_year': request.args.get('academic_year')
    }
    
    if not query:
        return jsonify([])
    
    results = search_service.search_syllabuses(query, search_type=search_type, filters=filters)
    return jsonify(results), 200

@search_bp.route('/ocr', methods=['POST'])
@inject
def process_ocr(ocr_service: OCRService = Provide[Container.ocr_service]):
    """
    Process an uploaded file with OCR and return text.
    ---
    tags:
      - Search
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: PDF or Image file to OCR
    responses:
      200:
        description: Extracted text
      400:
        description: Missing file
      500:
        description: OCR processing error
    """
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
        
    # Temporary save
    temp_dir = "temp_ocr"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    file.save(file_path)
    
    try:
        text = ocr_service.process_file(file_path)
        # Clean up
        os.remove(file_path)
        return jsonify({'text': text}), 200
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'message': str(e)}), 500

@search_bp.route('/reindex', methods=['POST'])
@inject
def reindex_all(search_service: SearchService = Provide[Container.search_service],
                syllabus_service = Provide[Container.syllabus_service]):
    """
    Manually trigger reindexing of all syllabuses into Elasticsearch.
    ---
    tags:
      - Search
    responses:
      200:
        description: Reindexing status
    """
    syllabuses = syllabus_service.list_syllabuses()
    count = 0
    for s in syllabuses:
        content = {
            "subject_code": s.subject.code if s.subject else "",
            "subject_name_vi": s.subject.name_vi if s.subject else "",
            "description": s.description or "",
            "version": s.version,
            "status": s.status,
            "content": f"{s.description or ''} {s.subject.name_vi if s.subject else ''}"
        }
        if search_service.index_syllabus(s.id, content):
            count += 1
            
    return jsonify({'message': f'Reindexed {count} syllabuses'}), 200
