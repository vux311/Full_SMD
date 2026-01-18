"""
RBAC Quick Test - Chỉ test permissions, không test workflow
"""

import requests
import json

BASE_URL = "http://localhost:5000"

TEST_USERS = {
    'admin': {'username': 'admin', 'password': '123456'},
    'lecturer': {'username': 'gv_se', 'password': '123456'},
    'hod': {'username': 'hod_se', 'password': '123456'},
    'aa': {'username': 'aa_user', 'password': '123456'},
    'student': {'username': 'sv_hcmut', 'password': '123456'},
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def login(username, password):
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={'username': username, 'password': password}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token'), data.get('role')
        return None, None
    except Exception as e:
        print(f"{Colors.RED}Login error: {e}{Colors.END}")
        return None, None

def test_permission(method, endpoint, token, should_pass, description):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    try:
        if method == 'GET':
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == 'POST':
            response = requests.post(f"{BASE_URL}{endpoint}", json={}, headers=headers)
        
        status = response.status_code
        
        # Check permission (403 = no permission, anything else = has permission to try)
        has_permission = (status != 403)
        
        if should_pass and has_permission:
            print(f"  {Colors.GREEN}✓{Colors.END} {description}: Has permission (status {status})")
            return True
        elif not should_pass and not has_permission:
            print(f"  {Colors.GREEN}✓{Colors.END} {description}: Correctly blocked (403)")
            return True
        else:
            print(f"  {Colors.RED}✗{Colors.END} {description}: Expected {'access' if should_pass else 'block'}, got status {status}")
            return False
    except Exception as e:
        print(f"  {Colors.RED}✗{Colors.END} {description}: Error - {e}")
        return False

def run_tests():
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}RBAC PERMISSION TEST (Quick){Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    tokens = {}
    
    print(f"{Colors.YELLOW}>>> Login Test Users{Colors.END}")
    for key, creds in TEST_USERS.items():
        token, role = login(creds['username'], creds['password'])
        if token:
            tokens[key] = token
            print(f"{Colors.GREEN}✓{Colors.END} {key}: {role}")
    
    if len(tokens) < 5:
        print(f"\n{Colors.RED}Not all users logged in. Check credentials.{Colors.END}")
        return
    
    passed = 0
    total = 0
    
    # Test 1: User List (Admin only)
    print(f"\n{Colors.YELLOW}>>> Test 1: User List (GET /users/) - Admin Only{Colors.END}")
    tests = [
        ('admin', True, "Admin should access"),
        ('lecturer', False, "Lecturer should be blocked"),
        ('hod', False, "HOD should be blocked"),
        ('aa', False, "AA should be blocked"),
        ('student', False, "Student should be blocked"),
    ]
    for role_key, should_pass, desc in tests:
        if role_key in tokens:
            total += 1
            if test_permission('GET', '/users/', tokens[role_key], should_pass, desc):
                passed += 1
    
    # Test 2: Syllabus Submit (Lecturer, Admin)
    print(f"\n{Colors.YELLOW}>>> Test 2: Syllabus Submit (POST /syllabuses/1/submit) - Lecturer, Admin{Colors.END}")
    tests = [
        ('admin', True, "Admin should access"),
        ('lecturer', True, "Lecturer should access"),
        ('hod', False, "HOD should be blocked"),
        ('aa', False, "AA should be blocked"),
        ('student', False, "Student should be blocked"),
    ]
    for role_key, should_pass, desc in tests:
        if role_key in tokens:
            total += 1
            if test_permission('POST', '/syllabuses/1/submit', tokens[role_key], should_pass, desc):
                passed += 1
    
    # Test 3: Syllabus Evaluate (HOD, AA, Admin)
    print(f"\n{Colors.YELLOW}>>> Test 3: Syllabus Evaluate (POST /syllabuses/1/evaluate) - HOD, AA, Admin{Colors.END}")
    tests = [
        ('admin', True, "Admin should access"),
        ('hod', True, "HOD should access"),
        ('aa', True, "AA should access"),
        ('lecturer', False, "Lecturer should be blocked"),
        ('student', False, "Student should be blocked"),
    ]
    for role_key, should_pass, desc in tests:
        if role_key in tokens:
            total += 1
            if test_permission('POST', '/syllabuses/1/evaluate', tokens[role_key], should_pass, desc):
                passed += 1
    
    # Test 4: Student Subscribe (Student, Admin)
    print(f"\n{Colors.YELLOW}>>> Test 4: Student Subscribe (POST /student/subscribe) - Student, Admin{Colors.END}")
    tests = [
        ('admin', True, "Admin should access"),
        ('student', True, "Student should access"),
        ('lecturer', False, "Lecturer should be blocked"),
        ('hod', False, "HOD should be blocked"),
        ('aa', False, "AA should be blocked"),
    ]
    for role_key, should_pass, desc in tests:
        if role_key in tokens:
            total += 1
            if test_permission('POST', '/student/subscribe', tokens[role_key], should_pass, desc):
                passed += 1
    
    # Test 5: Admin Logs (Admin only)
    print(f"\n{Colors.YELLOW}>>> Test 5: Admin Logs (GET /admin/logs) - Admin Only{Colors.END}")
    tests = [
        ('admin', True, "Admin should access"),
        ('lecturer', False, "Lecturer should be blocked"),
        ('hod', False, "HOD should be blocked"),
        ('aa', False, "AA should be blocked"),
        ('student', False, "Student should be blocked"),
    ]
    for role_key, should_pass, desc in tests:
        if role_key in tokens:
            total += 1
            if test_permission('GET', '/admin/logs', tokens[role_key], should_pass, desc):
                passed += 1
    
    # Test 6: Program Outcome Create (AA, Admin)
    print(f"\n{Colors.YELLOW}>>> Test 6: Program Outcome Create (POST /program-outcomes/) - AA, Admin{Colors.END}")
    tests = [
        ('admin', True, "Admin should access"),
        ('aa', True, "AA should access"),
        ('lecturer', False, "Lecturer should be blocked"),
        ('hod', False, "HOD should be blocked"),
        ('student', False, "Student should be blocked"),
    ]
    for role_key, should_pass, desc in tests:
        if role_key in tokens:
            total += 1
            if test_permission('POST', '/program-outcomes/', tokens[role_key], should_pass, desc):
                passed += 1
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}RBAC PERMISSION TEST RESULTS{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"\n{Colors.GREEN if passed == total else Colors.YELLOW}Passed: {passed}/{total} tests{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{'🎉 ' * 10}{Colors.END}")
        print(f"{Colors.GREEN}ALL RBAC TESTS PASSED! System is secure! 🔒{Colors.END}")
        print(f"{Colors.GREEN}{'🎉 ' * 10}{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Review permissions.{Colors.END}\n")

if __name__ == '__main__':
    print("\n⚠️  Make sure the API server is running on http://localhost:5000")
    input("\nPress Enter to start RBAC permission tests...")
    run_tests()
