# 🔧 QUICK FIX CHECKLIST - Syllabus Management System

## ✅ Ready-to-Apply Fixes

### Priority 1: CRITICAL (Apply Immediately)

#### ☐ Fix #1: Remove Duplicate AiService Definition
**File:** `apps/api/src/dependency_container.py`  
**Action:** 
- Find and DELETE lines with duplicate `ai_service = providers.Factory(AiService)` (second definition)
- Keep ONLY the first definition with `audit_repository=ai_auditlog_repository`

**Before:**
```python
# Line ~362
ai_service = providers.Factory(
    AiService,
    audit_repository=ai_auditlog_repository
)

# ... other code ...

# Line ~370 (DELETE THIS!)
from services.ai_service import AiService
ai_service = providers.Factory(
    AiService
)
```

**After:**
```python
# Keep ONLY this:
from services.ai_service import AiService
ai_service = providers.Factory(
    AiService,
    audit_repository=ai_auditlog_repository
)
```

---

#### ☐ Fix #2: Change Database Session from Singleton to Factory
**File:** `apps/api/src/dependency_container.py`  
**Action:**
- Change `db_session = providers.Object(session)` to `db_session = providers.Factory(...)`

**Before:**
```python
from infrastructure.databases.mssql import session
db_session = providers.Object(session)  # ❌ Singleton
```

**After:**
```python
from infrastructure.databases.mssql import SessionLocal
db_session = providers.Factory(SessionLocal)  # ✅ Factory (new instance per injection)
```

---

#### ☐ Fix #3: Update mssql.py with Connection Pool Config
**File:** `apps/api/src/infrastructure/databases/mssql.py`  
**Action:**
- Replace entire `engine` creation with pooled version
- Add `SessionLocal` export

**Before:**
```python
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
```

**After:**
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

def init_mssql(app):
    try:
        Base.metadata.create_all(bind=engine)
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")
        raise
```

---

### Priority 2: HIGH (Apply within 24 hours)

#### ☐ Fix #4: Fix SyllabusService.submit_syllabus() Logic
**File:** `apps/api/src/services/syllabus_service.py`  
**Action:**
- Replace the entire `submit_syllabus()` method

**Find this section:**
```python
def submit_syllabus(self, id: int, user_id: int):
    s = self.repository.get_by_id(id)
    if not s:
        return None
    
    current_status = (s.status or '').upper()
    if current_status not in ('DRAFT', 'REJECTED', 'RETURNED'):
         raise ValueError(f'Syllabus cannot be submitted in current status: {s.status}')
    ...
```

**Replace with:**
```python
def submit_syllabus(self, id: int, user_id: int):
    """Submit syllabus for evaluation. Can only submit from DRAFT or REJECTED status."""
    s = self.repository.get_by_id(id)
    if not s:
        return None
    
    current_status = (s.status or '').upper()
    valid_states = ('DRAFT', 'REJECTED')  # Remove 'RETURNED'
    
    if current_status not in valid_states:
        raise ValueError(
            f'Cannot submit syllabus in {current_status} status. '
            f'Valid states for submission: {valid_states}'
        )
    
    from_status = s.status
    updated = self.repository.update(id, {'status': 'PENDING'})
    
    if self.workflow_log_repository:
        self.workflow_log_repository.create({
            'syllabus_id': id,
            'actor_id': user_id,
            'action': 'SUBMIT',
            'from_status': from_status,
            'to_status': 'PENDING',
            'comment': None
        })
    return updated
```

---

#### ☐ Fix #5: Add @token_required to Workflow Endpoints
**File:** `apps/api/src/api/controllers/syllabus_controller.py`  
**Action:**
- Add `@token_required` decorator to these endpoints:
  - `submit_syllabus()`
  - `evaluate_syllabus()` (if exists)
  - Any other admin/workflow endpoints

**Example - Find this:**
```python
@syllabus_bp.route('/<int:id>/submit', methods=['POST'])
@inject
def submit_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
```

**Change to:**
```python
@syllabus_bp.route('/<int:id>/submit', methods=['POST'])
@token_required  # ✅ ADD THIS LINE
@inject
def submit_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
```

---

#### ☐ Fix #6: Add Error Handling to AI Controller
**File:** `apps/api/src/api/controllers/ai_controller.py`  
**Action:**
- Wrap the entire function body in try-except

**Find this:**
```python
@ai_bp.route('/generate', methods=['POST'])
@inject
def generate(ai_service: AiService = Provide[Container.ai_service]):
    data = request.get_json() or {}
    subject_name = data.get('subject_name')
    if not subject_name:
        return jsonify({'message': 'subject_name is required'}), 400

    res = ai_service.generate(subject_name)
    if isinstance(res, dict) and res.get('error'):
        return jsonify({'message': res.get('error')}), 500

    return jsonify(res), 200
```

**Replace with:**
```python
@ai_bp.route('/generate', methods=['POST'])
@inject
def generate(ai_service: AiService = Provide[Container.ai_service]):
    try:
        data = request.get_json() or {}
        subject_name = data.get('subject_name', '').strip()
        
        if not subject_name:
            return jsonify({'message': 'subject_name is required'}), 400

        res = ai_service.generate(subject_name)
        
        # Validate response type
        if not isinstance(res, dict):
            return jsonify({'message': 'Invalid response from AI service'}), 500
        
        if res.get('error'):
            return jsonify({'message': res.get('error')}), 400
        
        return jsonify(res), 200
    
    except Exception as e:
        return jsonify({'message': f'AI generation error: {str(e)}'}), 500
```

---

### Priority 3: MEDIUM (Apply within 1 week)

#### ☐ Fix #7: Improve Exception Handling in app.py
**File:** `apps/api/src/app.py`  
**Action:**
- Replace generic `except Exception: pass` with proper logging

**Find this:**
```python
try:
    container.wire(modules=[...])
except Exception:
    pass
```

**Replace with:**
```python
try:
    container.wire(modules=[...])
except Exception as e:
    app.logger.error(f"DI wiring failed: {e}", exc_info=True)
    import os
    if os.getenv('ENVIRONMENT') == 'production':
        raise
```

---

#### ☐ Fix #8: Add User Input Validation to UserRepository
**File:** `apps/api/src/infrastructure/repositories/user_repository.py`  
**Action:**
- Enhance `get_by_username()` method

**Find this:**
```python
def get_by_username(self, username: str) -> Optional[User]:
    return self.session.query(User).filter_by(username=username).first()
```

**Replace with:**
```python
def get_by_username(self, username: str) -> Optional[User]:
    if not username or not isinstance(username, str):
        return None
    username = username.strip()
    if not username:
        return None
    return self.session.query(User).filter_by(username=username).first()
```

---

## 📋 Verification Checklist

After applying fixes, verify:

- [ ] App starts without errors: `python -m flask run`
- [ ] DI wiring shows success message (check logs)
- [ ] POST /auth/login works
- [ ] POST /syllabuses/{id}/submit requires auth token
- [ ] POST /ai/generate handles errors gracefully
- [ ] No duplicate service registrations in container
- [ ] Database connection works (test any DB query)
- [ ] Multiple concurrent requests don't share session state

---

## 🧪 Quick Test Commands

```bash
# Test 1: App startup
cd apps/api/src
python -c "from app import create_app; app = create_app(); print('✓ App created successfully')"

# Test 2: DI Container
python -c "from dependency_container import Container; c = Container(); print('✓ Container initialized')"

# Test 3: Database
python -c "from infrastructure.databases.mssql import SessionLocal; s = SessionLocal(); print('✓ Session created'); s.close()"

# Test 4: API call (if app running)
curl -X POST http://localhost:5000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"subject_name": "Python Programming"}'
```

---

## 📞 Support

If any fix causes issues:
1. Check error logs: `tail -f app.log`
2. Verify imports: `python -c "from [module] import [class]"`
3. Check Python version: `python --version` (should be 3.8+)
4. Check dependencies: `pip list | grep dependency-injector`

---

**Last Updated:** 2026-01-13  
**Status:** Ready for implementation ✅
