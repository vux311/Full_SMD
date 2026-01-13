import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # apps/api/src

from services.program_outcome_service import ProgramOutcomeService

class StubRepo:
    def __init__(self):
        self.created = {}
    def create(self, data):
        self.created = data
        return data
    def update(self, id, data):
        return {'id': id, **data}
    def delete(self, id):
        return True

class StubProgramRepo:
    def __init__(self, exists=True):
        self.exists = exists
    def get_by_id(self, id):
        return {'id': id} if self.exists else None


def test_create_plo_requires_valid_program():
    repo = StubRepo()
    program_repo = StubProgramRepo(exists=False)
    svc = ProgramOutcomeService(repository=repo, program_repository=program_repo)
    try:
        svc.create_plo({'program_id': 1, 'code': 'PLO1', 'description': 'd'})
        assert False, 'Should have raised ValueError'
    except ValueError:
        pass

    program_repo = StubProgramRepo(exists=True)
    svc = ProgramOutcomeService(repository=repo, program_repository=program_repo)
    item = svc.create_plo({'program_id': 1, 'code': 'PLO1', 'description': 'd'})
    assert repo.created['code'] == 'PLO1'


def test_update_and_delete_delegates_to_repo():
    repo = StubRepo()
    svc = ProgramOutcomeService(repository=repo)
    updated = svc.update_plo(1, {'code': 'X'})
    assert updated['id'] == 1
    assert svc.delete_plo(1) is True