"""
RBAC Implementation Test Script
Test role-based access control for different roles
"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Test credentials (from seed_all_data.py)
TEST_USERS = {
    'admin': {'username': 'admin', 'password': '123456', 'expected_role': 'Admin'},
    'lecturer': {'username': 'gv_se', 'password': '123456', 'expected_role': 'Lecturer'},
    'hod': {'username': 'hod_se', 'password': '123456', 'expected_role': 'Head of Dept'},
    'aa': {'username': 'aa_user', 'password': '123456', 'expected_role': 'Academic Affairs'},
    'student': {'username': 'sv_hcmut', 'password': '123456', 'expected_role': 'Student'},
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def login(username, password):
    """Login and return access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={'username': username, 'password': password},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            role = data.get('role')
            print(f"{Colors.GREEN}✓{Colors.END} Login successful: {username} ({role})")
            return token, role
        else:
            print(f"{Colors.RED}✗{Colors.END} Login failed: {response.json()}")
            return None, None
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} Login error: {e}")
        return None, None

def test_endpoint(method, endpoint, token, expected_status, description, data=None):
    """Test an endpoint with given token and expected status"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        if method == 'GET':
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == 'POST':
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(f"{BASE_URL}{endpoint}", json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(f"{BASE_URL}{endpoint}", headers=headers)
        
        status = response.status_code
        success = (status == expected_status)
        
        if success:
            print(f"  {Colors.GREEN}✓{Colors.END} {description}: {status} (expected {expected_status})")
        else:
            msg = response.json().get('message', '') if response.text else ''
            print(f"  {Colors.RED}✗{Colors.END} {description}: {status} (expected {expected_status}) - {msg}")
        
        return success
    except Exception as e:
        print(f"  {Colors.RED}✗{Colors.END} {description}: Error - {e}")
        return False

def create_test_syllabus(token, status='DRAFT'):
    """Create a test syllabus for testing"""
    try:
        data = {
            'subject_id': 1,
            'academic_year_id': 1,
            'lecturer_id': 2,  # gv_se
            'status': status,
            'version': '1.0-TEST',
            'description': 'Test syllabus for RBAC'
        }
        response = requests.post(
            f"{BASE_URL}/syllabuses/",
            json=data,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        if response.status_code == 201:
            syllabus = response.json()
            return syllabus.get('id')
        return None
    except Exception as e:
        print(f"  {Colors.YELLOW}⚠{Colors.END} Could not create test syllabus: {e}")
        return None

def update_syllabus_status(syllabus_id, token, status):
    """Update syllabus status for testing"""
    try:
        response = requests.put(
            f"{BASE_URL}/syllabuses/{syllabus_id}",
            json={'status': status},
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        return response.status_code == 200
    except:
        return False

def run_tests():
    """Run comprehensive RBAC tests"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}RBAC IMPLEMENTATION TEST{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    tokens = {}
    
    # Login all test users
    print(f"\n{Colors.YELLOW}>>> Phase 1: Login Test Users{Colors.END}")
    for key, creds in TEST_USERS.items():
        token, role = login(creds['username'], creds['password'])
        if token:
            tokens[key] = token
    
    if not tokens:
        print(f"\n{Colors.RED}No users logged in. Cannot proceed with tests.{Colors.END}")
        return
    
    # Create test syllabuses with appropriate statuses
    print(f"\n{Colors.YELLOW}>>> Phase 2: Create Test Data{Colors.END}")
    draft_syllabus_id = None
    pending_syllabus_id = None
    
    if 'admin' in tokens:
        # Create DRAFT syllabus for submit test
        draft_syllabus_id = create_test_syllabus(tokens['admin'], 'DRAFT')
        if draft_syllabus_id:
            print(f"{Colors.GREEN}✓{Colors.END} Created DRAFT syllabus (ID: {draft_syllabus_id})")
        
        # Create PENDING syllabus for evaluate test
        pending_syllabus_id = create_test_syllabus(tokens['admin'], 'PENDING')
        if pending_syllabus_id:
            print(f"{Colors.GREEN}✓{Colors.END} Created PENDING syllabus (ID: {pending_syllabus_id})")
    
    if not draft_syllabus_id:
        draft_syllabus_id = 1  # Fallback
        print(f"{Colors.YELLOW}⚠{Colors.END} Using existing syllabus ID: {draft_syllabus_id}")
    
    if not pending_syllabus_id:
        pending_syllabus_id = 1  # Fallback
        print(f"{Colors.YELLOW}⚠{Colors.END} Using existing syllabus ID: {pending_syllabus_id}")
    
    # Test 1: Syllabus Submit (Lecturer/Admin only)
    print(f"\n{Colors.YELLOW}>>> Test 1: Syllabus Submit (POST /syllabuses/{draft_syllabus_id}/submit){Colors.END}")
    print(f"Expected: Lecturer ✓, Admin ✓, Others ✗")
    
    # Reset to DRAFT if needed
    if 'admin' in tokens:
        update_syllabus_status(draft_syllabus_id, tokens['admin'], 'DRAFT')
    
    if 'lecturer' in tokens:
        test_endpoint('POST', f'/syllabuses/{draft_syllabus_id}/submit', tokens['lecturer'], 200, 
                      "Lecturer submit", {})
    
    # Reset to DRAFT for admin test
    if 'admin' in tokens:
        update_syllabus_status(draft_syllabus_id, tokens['admin'], 'DRAFT')
        test_endpoint('POST', f'/syllabuses/{draft_syllabus_id}/submit', tokens['admin'], 200, 
                      "Admin submit", {})
    
    if 'student' in tokens:
        test_endpoint('POST', f'/syllabuses/{draft_syllabus_id}/submit', tokens['student'], 403, 
                      "Student submit (should fail)", {})
    if 'hod' in tokens:
        test_endpoint('POST', f'/syllabuses/{draft_syllabus_id}/submit', tokens['hod'], 403, 
                      "HOD submit (should fail)", {})
    
    # Test 2: Syllabus Evaluate (HOD/AA/Admin only)
    print(f"\n{Colors.YELLOW}>>> Test 2: Syllabus Evaluate (POST /syllabuses/{pending_syllabus_id}/evaluate){Colors.END}")
    print(f"Expected: HOD ✓, AA ✓, Admin ✓, Others ✗")
    
    # Reset to PENDING if needed
    if 'admin' in tokens:
        update_syllabus_status(pending_syllabus_id, tokens['admin'], 'PENDING')
    
    if 'hod' in tokens:
        test_endpoint('POST', f'/syllabuses/{pending_syllabus_id}/evaluate', tokens['hod'], 200, 
                      "HOD evaluate", {'action': 'approve'})
    
    # Reset to PENDING for AA test
    if 'admin' in tokens:
        update_syllabus_status(pending_syllabus_id, tokens['admin'], 'PENDING')
    
    if 'aa' in tokens:
        test_endpoint('POST', f'/syllabuses/{pending_syllabus_id}/evaluate', tokens['aa'], 200, 
                      "AA evaluate", {'action': 'approve'})
    
    # Reset to PENDING for Admin test
    if 'admin' in tokens:
        update_syllabus_status(pending_syllabus_id, tokens['admin'], 'PENDING')
        test_endpoint('POST', f'/syllabuses/{pending_syllabus_id}/evaluate', tokens['admin'], 200, 
                      "Admin evaluate", {'action': 'approve'})
    
    if 'lecturer' in tokens:
        test_endpoint('POST', f'/syllabuses/{pending_syllabus_id}/evaluate', tokens['lecturer'], 403, 
                      "Lecturer evaluate (should fail)", {'action': 'approve'})
    if 'student' in tokens:
        test_endpoint('POST', f'/syllabuses/{pending_syllabus_id}/evaluate', tokens['student'], 403, 
                      "Student evaluate (should fail)", {'action': 'approve'})
    
    # Test 3: User Management (Admin only)
    print(f"\n{Colors.YELLOW}>>> Test 3: User List (GET /users/){Colors.END}")
    print(f"Expected: Admin ✓, Others ✗")
    
    if 'admin' in tokens:
        test_endpoint('GET', '/users/', tokens['admin'], 200, "Admin list users")
    if 'lecturer' in tokens:
        test_endpoint('GET', '/users/', tokens['lecturer'], 403, "Lecturer list users (should fail)")
    if 'student' in tokens:
        test_endpoint('GET', '/users/', tokens['student'], 403, "Student list users (should fail)")
    
    # Test 4: Student Subscribe (Student/Admin only)
    print(f"\n{Colors.YELLOW}>>> Test 4: Student Subscribe (POST /student/subscribe){Colors.END}")
    print(f"Expected: Student ✓, Admin ✓, Others ✗")
    
    if 'student' in tokens:
        test_endpoint('POST', '/student/subscribe', tokens['student'], 201, 
                      "Student subscribe", {'student_id': 1, 'subject_id': 1})
    if 'admin' in tokens:
        test_endpoint('POST', '/student/subscribe', tokens['admin'], 201, 
                      "Admin subscribe", {'student_id': 1, 'subject_id': 1})
    if 'lecturer' in tokens:
        test_endpoint('POST', '/student/subscribe', tokens['lecturer'], 403, 
                      "Lecturer subscribe (should fail)", {'student_id': 1, 'subject_id': 1})
    
    # Test 5: Admin Logs (Admin only)
    print(f"\n{Colors.YELLOW}>>> Test 5: Admin Logs (GET /admin/logs){Colors.END}")
    print(f"Expected: Admin ✓, Others ✗")
    
    if 'admin' in tokens:
        test_endpoint('GET', '/admin/logs', tokens['admin'], 200, "Admin view logs")
    if 'hod' in tokens:
        test_endpoint('GET', '/admin/logs', tokens['hod'], 403, "HOD view logs (should fail)")
    if 'student' in tokens:
        test_endpoint('GET', '/admin/logs', tokens['student'], 403, "Student view logs (should fail)")
    
    # Test 6: Program Outcome Create (AA/Admin only)
    print(f"\n{Colors.YELLOW}>>> Test 6: Program Outcome Create (POST /program-outcomes/){Colors.END}")
    print(f"Expected: AA ✓, Admin ✓, Others ✗")
    
    plo_data = {'program_id': 1, 'code': 'PLO_TEST', 'description': 'Test PLO'}
    
    if 'aa' in tokens:
        test_endpoint('POST', '/program-outcomes/', tokens['aa'], 201, 
                      "AA create PLO", plo_data)
    if 'admin' in tokens:
        test_endpoint('POST', '/program-outcomes/', tokens['admin'], 201, 
                      "Admin create PLO", plo_data)
    if 'lecturer' in tokens:
        test_endpoint('POST', '/program-outcomes/', tokens['lecturer'], 403, 
                      "Lecturer create PLO (should fail)", plo_data)
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.GREEN}RBAC Test Completed!{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")

if __name__ == '__main__':
    print("\n⚠️  Make sure the API server is running on http://localhost:5000")
    print("⚠️  Make sure you have seeded the database with test users")
    input("\nPress Enter to start tests...")
    run_tests()
