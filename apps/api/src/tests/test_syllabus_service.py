import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # apps/api/src

import json
from services.syllabus_service import SyllabusService


class StubRepo:
    def __init__(self):
        self.created = []

    def create(self, data):
        # simulate DB model with id and status
        class Item:
            pass
        item = Item()
        item.id = 123
        item.status = data.get('status', 'DRAFT')
        self.created.append(data)
        return item

    def get_by_id(self, id):
        return None


class StubFKRepo:
    def __init__(self, exists=True):
        self.exists = exists

    def get_by_id(self, id):
        return {'id': id} if self.exists else None


class StubChildRepo:
    def __init__(self):
        self.items = []

    def create(self, data):
        self.items.append(data)
        class Item:
            def __init__(self, data, id):
                self.__dict__.update(data)
                self.id = id
        return Item(data, len(self.items))


def test_create_syllabus_creates_child_entities_and_serializes_time_allocation():
    repo = StubRepo()
    subj = StubFKRepo(True)
    prog = StubFKRepo(True)
    ay = StubFKRepo(True)
    user = StubFKRepo(True)
    clo_repo = StubChildRepo()
    mat_repo = StubChildRepo()
    plan_repo = StubChildRepo()
    scheme_repo = StubChildRepo()
    comp_repo = StubChildRepo()
    rubric_repo = StubChildRepo()

    svc = SyllabusService(
        repository=repo,
        subject_repository=subj,
        program_repository=prog,
        academic_year_repository=ay,
        user_repository=user,
        syllabus_clo_repository=clo_repo,
        syllabus_material_repository=mat_repo,
        teaching_plan_repository=plan_repo,
        assessment_scheme_repository=scheme_repo,
        assessment_component_repository=comp_repo,
        rubric_repository=rubric_repo
    )

    payload = {
        'subject_id': 1,
        'program_id': 1,
        'academic_year_id': 1,
        'lecturer_id': 1,
        'time_allocation': {'theory': 10, 'practice': 20},
        'clos': [{'code': 'C1', 'description': 'desc'}],
        'materials': [{'type': 'MAIN', 'title': 't'}],
        'teaching_plans': [{'week': 1, 'topic': 't'}],
        'assessment_schemes': [
            {
                'name': 'Scheme1',
                'weight': 50,
                'components': [
                    {'name': 'Comp1', 'weight': 100, 'rubrics': [{'criteria': 'r', 'max_score': 10}]}
                ]
            }
        ]
    }

    result = svc.create_syllabus(payload.copy())
    # header created
    assert result.id == 123
    # child repos created
    assert len(clo_repo.items) == 1
    assert len(mat_repo.items) == 1
    assert len(plan_repo.items) == 1
    assert len(scheme_repo.items) == 1
    assert len(comp_repo.items) == 1
    assert len(rubric_repo.items) == 1

    # ensure time_allocation was serialized as JSON in the header create payload
    header_payload = repo.created[0]
    assert isinstance(header_payload['time_allocation'], str)
    parsed = json.loads(header_payload['time_allocation'])
    assert parsed['theory'] == 10


def test_submit_syllabus_allows_returned_case_insensitive():
    class GetRepo:
        def __init__(self, status):
            class Item:
                pass
            self.item = Item()
            self.item.status = status
        def get_by_id(self, id):
            return self.item
        def update(self, id, data):
            return data

    for status in ['returned', 'RETURNED', 'Returned']:
        repo = GetRepo(status)
        svc = SyllabusService(repository=repo)
        updated = svc.submit_syllabus(1, 2)
        assert updated == {'status': 'PENDING'}