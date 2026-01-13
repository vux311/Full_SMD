"""End-to-end happy-path test for Syllabus Management System

Run this script directly (python tests/e2e_test_flow.py).
Requires: requests, colorama

It will stop immediately and print an error in red if any step returns an unexpected status code.
"""

import sys
import time
import uuid
from datetime import date

import requests
import json
try:
    from colorama import Fore, Style, init as colorama_init
except Exception:
    print("Please install 'colorama' (pip install colorama) to run this script.")
    sys.exit(2)

colorama_init(autoreset=True)

BASE_URL = 'http://localhost:9999'


def log(step: str, message: str, status: str = 'INFO'):
    """Nicely print a log line.

    status: INFO, OK, FAIL
    """
    status = status.upper()
    if status == 'OK':
        color = Fore.GREEN
    elif status == 'FAIL':
        color = Fore.RED
    else:
        color = Fore.CYAN
    print(f"[{color}{status}{Style.RESET_ALL}] {step} - {message}")


def fail(step: str, message: str, resp=None):
    log(step, message, 'FAIL')
    if resp is not None:
        try:
            print(Fore.RED + resp.text)
        except Exception:
            pass
    sys.exit(1)


def expect_status(step: str, resp: requests.Response, expected: int):
    if resp.status_code != expected:
        fail(step, f"Expected HTTP {expected}, got {resp.status_code}", resp)
    log(step, f"HTTP {resp.status_code}", 'OK')


def post(path: str, json: dict, token: str = None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return requests.post(BASE_URL + path, json=json, headers=headers)


def get(path: str, token: str = None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return requests.get(BASE_URL + path, headers=headers)


def run():
    # Step 1: Login admin
    step = '1. Login Admin'
    payload = {'username': 'admin', 'password': 'password123'}
    resp = post('/auth/login', payload)
    expect_status(step, resp, 200)
    token = resp.json().get('token')
    if not token:
        fail(step, 'No token returned', resp)
    log(step, 'Obtained token', 'OK')

    # Helper to generate short unique strings
    uid = str(uuid.uuid4())[:8]

    # Step 2: Create Faculty
    step = '2. Create Faculty'
    payload = {'code': f'E2E-FAC-{uid}', 'name': 'E2E Faculty'}
    resp = post('/faculties/', payload, token=token)
    expect_status(step, resp, 201)
    faculty_id = resp.json().get('id')

    # Step 3: Create Department
    step = '3. Create Department'
    payload = {'faculty_id': faculty_id, 'code': f'E2E-DEP-{uid}', 'name': 'E2E Department'}
    resp = post('/departments/', payload, token=token)
    expect_status(step, resp, 201)
    department_id = resp.json().get('id')

    # Step 4: Create Program
    step = '4. Create Program'
    payload = {'department_id': department_id, 'name': f'E2E Program {uid}', 'total_credits': 120}
    resp = post('/programs/', payload, token=token)
    expect_status(step, resp, 201)
    program_id = resp.json().get('id')

    # Step 5: Create Academic Year
    step = '5. Create Academic Year'
    payload = {'code': f'AY-{uid}', 'start_date': date.today().isoformat(), 'end_date': (date.today().replace(year=date.today().year + 1)).isoformat()}
    resp = post('/academic-years/', payload, token=token)
    expect_status(step, resp, 201)
    academic_year_id = resp.json().get('id')

    # Step 6: Create Lecturer (User)
    step = '6. Create Lecturer User'
    username = f'e2e_user_{uid}'
    payload = {'username': username, 'email': f'{username}@example.com', 'full_name': 'E2E Lecturer', 'password': 'pass1234'}
    resp = post('/users/', payload, token=token)
    expect_status(step, resp, 201)
    lecturer_id = resp.json().get('id')

    # Step 7: Create Subject
    step = '7. Create Subject'
    payload = {'department_id': department_id, 'code': f'E2E-SUB-{uid}', 'name_vi': 'E2E Môn học', 'name_en': 'E2E Subject', 'credits': 3}
    resp = post('/subjects/', payload, token=token)
    expect_status(step, resp, 201)
    subject_id = resp.json().get('id')

    # Step 8: Create Syllabus (Draft)
    step = '8. Create Syllabus (Draft)'
    payload = {'subject_id': subject_id, 'program_id': program_id, 'academic_year_id': academic_year_id, 'lecturer_id': lecturer_id}
    resp = post('/syllabuses/', payload, token=token)
    expect_status(step, resp, 201)
    syllabus = resp.json()
    syllabus_id = syllabus.get('id')
    if syllabus.get('status') and syllabus.get('status') != 'DRAFT':
        fail(step, f"Expected status DRAFT, got {syllabus.get('status')}")

    # Step 9: Add CLO
    step = '9. Add CLO'
    payload = {'syllabus_id': syllabus_id, 'code': 'CLO-1', 'description': 'Understand basics of E2E.'}
    resp = post('/syllabus-clos/', payload, token=token)
    expect_status(step, resp, 201)
    clo_id = resp.json().get('id')

    # Step 10: Add Assessment Scheme
    step = '10. Add Assessment Scheme'
    payload = {'syllabus_id': syllabus_id, 'name': 'Progress Test', 'weight': 50}
    resp = post('/assessment-schemes/', payload, token=token)
    expect_status(step, resp, 201)
    scheme_id = resp.json().get('id')

    # Step 11: Add Assessment Component
    step = '11. Add Assessment Component'
    payload = {'scheme_id': scheme_id, 'name': 'Quiz 1', 'weight': 10}
    resp = post('/assessment-components/', payload, token=token)
    expect_status(step, resp, 201)
    component_id = resp.json().get('id')

    # Step 12: Map CLO to Component
    step = '12. Map CLO to Component'
    payload = {'assessment_component_id': component_id, 'syllabus_clo_id': clo_id}
    resp = post('/assessment-clos/', payload, token=token)
    expect_status(step, resp, 201)

    # Step 13: Verify Details
    step = '13. Verify Details'
    resp = get(f'/syllabuses/{syllabus_id}/details', token=token)
    expect_status(step, resp, 200)
    detail = resp.json()
    # Debug: dump details
    try:
        print(Fore.CYAN + json.dumps(detail, indent=2, ensure_ascii=False))
    except Exception:
        pass
    # Check CLO presence
    clos = detail.get('clos', [])
    if not any(c.get('id') == clo_id for c in clos):
        fail(step, 'CLO not found in syllabus details')
    # Check component presence inside assessment_schemes
    # API returns camelCase via BaseSchema; support both for robustness
    schemes = detail.get('assessmentSchemes') or detail.get('assessment_schemes', [])
    found_comp = False
    for s in schemes:
        for c in s.get('components', []):
            if c.get('id') == component_id:
                found_comp = True
                break
        if found_comp:
            break
    if not found_comp:
        fail(step, 'Component not found in syllabus details')
    log(step, 'CLO and Component found in syllabus details', 'OK')

    # Step 14: Submit Syllabus
    step = '14. Submit Syllabus'
    payload = {'user_id': lecturer_id}
    resp = post(f'/syllabuses/{syllabus_id}/submit', payload, token=token)
    expect_status(step, resp, 200)
    s = resp.json()
    if s.get('status') != 'PENDING':
        fail(step, f"Expected status PENDING, got {s.get('status')}")

    # Step 15: Approve Syllabus
    step = '15. Approve Syllabus'
    payload = {'action': 'APPROVE', 'user_id': lecturer_id}
    resp = post(f'/syllabuses/{syllabus_id}/evaluate', payload, token=token)
    expect_status(step, resp, 200)
    s = resp.json()
    if s.get('status') != 'APPROVED':
        fail(step, f"Expected status APPROVED, got {s.get('status')}")

    log('E2E', f'Successfully completed happy-path for syllabus {syllabus_id}', 'OK')


if __name__ == '__main__':
    try:
        run()
    except requests.exceptions.ConnectionError as e:
        print(Fore.RED + 'Failed to connect to API at ' + BASE_URL)
        print(str(e))
        sys.exit(2)
