import os
import uuid
from werkzeug.utils import secure_filename
from infrastructure.repositories.file_repository import FileRepository

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

class FileService:
    def __init__(self, repository: FileRepository):
        self.repository = repository
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

    def _allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def upload_file(self, file_storage, uploader_id: int):
        if not file_storage or file_storage.filename == '':
            raise ValueError('No file selected')
        if not self._allowed_file(file_storage.filename):
            raise ValueError('File type not allowed')

        filename = secure_filename(file_storage.filename)
        unique_name = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_name)
        
        # Save to disk
        file_storage.save(file_path)

        # Save to DB
        file_data = {
            'uploader_id': uploader_id,
            'file_name': filename,
            'file_path': file_path,
            'mime_type': file_storage.mimetype,
            'file_size': 0 # Optional: implement size check
        }
        return self.repository.create(file_data)
        
    def get_file(self, id: int):
        return self.repository.get_by_id(id)