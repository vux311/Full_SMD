"""
Verification Script - Test All Applied Fixes
Run this script to verify that all fixes have been applied correctly.

Usage:
    cd apps/api/src
    python verify_fixes.py
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test 1: Verify all imports work."""
    print("\n=== Test 1: Imports ===")
    
    try:
        from dependency_container import Container
        print("✓ dependency_container imports successfully")
    except Exception as e:
        print(f"✗ dependency_container import failed: {e}")
        return False
    
    try:
        from infrastructure.databases.mssql import SessionLocal, engine
        print("✓ mssql imports successfully")
    except Exception as e:
        print(f"✗ mssql import failed: {e}")
        return False
    
    try:
        from domain.constants import WorkflowStatus
        print("✓ WorkflowStatus constants import successfully")
    except Exception as e:
        print(f"✗ WorkflowStatus import failed: {e}")
        return False
    
    try:
        from services.syllabus_service import SyllabusService
        print("✓ SyllabusService imports successfully")
    except Exception as e:
        print(f"✗ SyllabusService import failed: {e}")
        return False
    
    return True


def test_container_configuration():
    """Test 2: Verify DI Container configuration."""
    print("\n=== Test 2: DI Container Configuration ===")
    
    try:
        from dependency_container import Container
        container = Container()
        print("✓ Container created successfully")
        
        # Check if db_session is Factory (not Object)
        if hasattr(container, 'db_session'):
            provider = container.db_session
            provider_type = str(type(provider))
            if 'Factory' in provider_type:
                print("✓ db_session is Factory (correct)")
            else:
                print(f"✗ db_session is {provider_type} (should be Factory)")
                return False
        
        # Check if ai_service exists
        if hasattr(container, 'ai_service'):
            print("✓ ai_service provider exists")
        else:
            print("✗ ai_service provider not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Container configuration test failed: {e}")
        return False


def test_session_isolation():
    """Test 3: Verify session isolation."""
    print("\n=== Test 3: Session Isolation ===")
    
    try:
        from infrastructure.databases.mssql import SessionLocal
        
        session1 = SessionLocal()
        session2 = SessionLocal()
        
        if session1 is not session2:
            print("✓ Sessions are isolated (different instances)")
            session1.close()
            session2.close()
            return True
        else:
            print("✗ Sessions are the same instance (should be different)")
            return False
            
    except Exception as e:
        print(f"✗ Session isolation test failed: {e}")
        return False


def test_workflow_constants():
    """Test 4: Verify workflow constants."""
    print("\n=== Test 4: Workflow Constants ===")
    
    try:
        from domain.constants import WorkflowStatus
        
        # Check all required states exist
        required_states = ['DRAFT', 'PENDING', 'APPROVED', 'REJECTED']
        for state in required_states:
            if hasattr(WorkflowStatus, state):
                print(f"✓ WorkflowStatus.{state} exists")
            else:
                print(f"✗ WorkflowStatus.{state} missing")
                return False
        
        # Check valid state tuples
        if hasattr(WorkflowStatus, 'VALID_FOR_SUBMISSION'):
            valid = WorkflowStatus.VALID_FOR_SUBMISSION
            if 'DRAFT' in valid and 'REJECTED' in valid:
                print(f"✓ VALID_FOR_SUBMISSION correct: {valid}")
            else:
                print(f"✗ VALID_FOR_SUBMISSION incorrect: {valid}")
                return False
        else:
            print("✗ VALID_FOR_SUBMISSION not defined")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Workflow constants test failed: {e}")
        return False


def test_service_logic():
    """Test 5: Verify SyllabusService logic improvements."""
    print("\n=== Test 5: SyllabusService Logic ===")
    
    try:
        from services.syllabus_service import SyllabusService
        import inspect
        
        # Check submit_syllabus method signature and docstring
        if hasattr(SyllabusService, 'submit_syllabus'):
            method = getattr(SyllabusService, 'submit_syllabus')
            docstring = inspect.getdoc(method)
            
            if docstring and 'DRAFT or REJECTED' in docstring:
                print("✓ submit_syllabus has updated docstring")
            else:
                print("⚠ submit_syllabus docstring might need update")
            
            # Check source code for 'RETURNED'
            source = inspect.getsource(method)
            if 'RETURNED' in source:
                print("✗ submit_syllabus still contains 'RETURNED' reference")
                return False
            else:
                print("✓ submit_syllabus no longer references 'RETURNED'")
        else:
            print("✗ submit_syllabus method not found")
            return False
        
        # Check evaluate_syllabus method
        if hasattr(SyllabusService, 'evaluate_syllabus'):
            method = getattr(SyllabusService, 'evaluate_syllabus')
            source = inspect.getsource(method)
            
            if 'PENDING' in source:
                print("✓ evaluate_syllabus checks for PENDING status")
            else:
                print("⚠ evaluate_syllabus might not check status")
        
        return True
        
    except Exception as e:
        print(f"✗ Service logic test failed: {e}")
        return False


def test_controller_decorators():
    """Test 6: Verify @token_required decorators."""
    print("\n=== Test 6: Controller Decorators ===")
    
    try:
        from api.controllers.syllabus_controller import submit_syllabus, evaluate_syllabus
        import inspect
        
        # Check submit_syllabus for @token_required
        source = inspect.getsource(submit_syllabus)
        if '@token_required' in source:
            print("✓ submit_syllabus has @token_required decorator")
        else:
            print("✗ submit_syllabus missing @token_required decorator")
            return False
        
        # Check evaluate_syllabus for @token_required
        source = inspect.getsource(evaluate_syllabus)
        if '@token_required' in source:
            print("✓ evaluate_syllabus has @token_required decorator")
        else:
            print("✗ evaluate_syllabus missing @token_required decorator")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Controller decorators test failed: {e}")
        return False


def test_database_config():
    """Test 7: Verify database configuration."""
    print("\n=== Test 7: Database Configuration ===")
    
    try:
        from infrastructure.databases.mssql import engine
        
        # Check pool configuration
        pool = engine.pool
        pool_class = str(type(pool))
        
        if 'QueuePool' in pool_class:
            print(f"✓ Using QueuePool: {pool_class}")
        else:
            print(f"⚠ Not using QueuePool: {pool_class}")
        
        # Check pool size
        if hasattr(pool, '_pool'):
            print(f"✓ Pool configured with size: {pool.size()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Database config test failed: {e}")
        return False


def test_error_handling():
    """Test 8: Verify error handling improvements."""
    print("\n=== Test 8: Error Handling ===")
    
    try:
        from api.controllers.ai_controller import generate
        import inspect
        
        source = inspect.getsource(generate)
        
        # Check for try-except blocks
        if 'try:' in source and 'except' in source:
            print("✓ AI controller has try-except blocks")
        else:
            print("✗ AI controller missing error handling")
            return False
        
        # Check for logging
        if 'logger' in source or 'logging' in source:
            print("✓ AI controller has logging")
        else:
            print("⚠ AI controller might not have logging")
        
        # Check for input validation
        if 'strip()' in source:
            print("✓ AI controller validates input")
        else:
            print("⚠ AI controller might not validate input")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("VERIFICATION SCRIPT - Testing All Applied Fixes")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Container Configuration", test_container_configuration),
        ("Session Isolation", test_session_isolation),
        ("Workflow Constants", test_workflow_constants),
        ("Service Logic", test_service_logic),
        ("Controller Decorators", test_controller_decorators),
        ("Database Configuration", test_database_config),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Fixes verified successfully.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
