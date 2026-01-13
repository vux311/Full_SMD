from flask import Blueprint, request, jsonify, send_file
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.file_service import FileService
from api.schemas.file_schema import FileSchema
import os

file_bp = Blueprint('file', __name__, url_prefix='/files')
schema = FileSchema()

@file_bp.route('/upload', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def upload_file(service: FileService = Provide[Container.file_service]):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    # Demo: assume user_id=1 if no auth (In production, get from token)
    user_id = request.form.get('user_id', 1) 
    try:
        record = service.upload_file(file, int(user_id))
        return jsonify(schema.dump(record)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@file_bp.route('/<int:id>', methods=['GET'])
@inject
def download_file(id: int, service: FileService = Provide[Container.file_service]):
    record = service.get_file(id)
    if not record:
        return jsonify({'message': 'File not found'}), 404
    try:
        return send_file(os.path.abspath(record.file_path), as_attachment=True, download_name=record.file_name)
    except Exception:
        return jsonify({'message': 'File not found on disk'}), 404