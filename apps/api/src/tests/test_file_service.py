import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # apps/api/src

import os
import tempfile
from services.file_service import FileService, UPLOAD_FOLDER

class StubFileStorage:
    def __init__(self, filename, content=b"data", mimetype='application/octet-stream'):
        self.filename = filename
        self._content = content
        self.mimetype = mimetype

    def save(self, path):
        with open(path, 'wb') as f:
            f.write(self._content)


class StubRepo:
    def __init__(self):
        self.created = None
    def create(self, data):
        self.created = data
        class Item:
            def __init__(self, d):
                self.__dict__.update(d)
        return Item(data)


def test_upload_file_saves_to_disk_and_db(tmp_path, monkeypatch):
    # Use a temp upload folder
    tmp_dir = tmp_path / 'uploads'
    monkeypatch.setattr('services.file_service.UPLOAD_FOLDER', str(tmp_dir))

    repo = StubRepo()
    svc = FileService(repository=repo)

    file_storage = StubFileStorage('test.txt', b'hello', 'text/plain')
    record = svc.upload_file(file_storage, uploader_id=5)

    # Ensure file saved on disk
    assert os.path.exists(record.file_path)
    assert repo.created['uploader_id'] == 5
    assert repo.created['file_name'] == 'test.txt'


def test_upload_rejects_bad_extension():
    repo = StubRepo()
    svc = FileService(repository=repo)
    file_storage = StubFileStorage('test.exe')
    try:
        svc.upload_file(file_storage, uploader_id=1)
        assert False, 'Should raise ValueError for disallowed extension'
    except ValueError:
        pass