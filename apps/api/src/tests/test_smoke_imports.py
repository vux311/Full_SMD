import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # apps/api/src

from dependency_container import Container
from services.syllabus_service import SyllabusService
from services.program_outcome_service import ProgramOutcomeService
from services.file_service import FileService


def test_container_has_services():
    c = Container()
    assert hasattr(c, 'syllabus_service')
    assert hasattr(c, 'program_outcome_service')
    assert hasattr(c, 'file_service')


def test_service_classes_importable():
    assert callable(SyllabusService)
    assert callable(ProgramOutcomeService)
    assert callable(FileService)