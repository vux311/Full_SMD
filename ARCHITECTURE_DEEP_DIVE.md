# 🏗️ Architecture Deep Dive & Issue Mapping

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (Next.js)                        │
│              apps/web (React Components)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              API LAYER (Flask Blueprints)                   │
│  /api/controllers/{subject,syllabus,user,ai,...}            │
│                                                               │
│  ├─ @inject decorator (Dependency Injector)                 │
│  ├─ Provide[Container.{service}]                            │
│  ├─ Schema validation (Marshmallow)                         │
│  └─ @token_required (Auth middleware)                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│           SERVICE LAYER (Business Logic)                    │
│  SubjectService, SyllabusService, UserService, etc.         │
│                                                               │
│  ├─ Dependency: Repository (injected)                       │
│  ├─ Workflows (submit, evaluate, approve)                   │
│  ├─ Validation logic                                        │
│  └─ Transaction management                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│       REPOSITORY LAYER (Data Access)                        │
│  SubjectRepository, UserRepository, SyllabusRepository, etc. │
│                                                               │
│  ├─ Dependency: SQLAlchemy Session (injected)               │
│  ├─ Query building                                          │
│  ├─ ORM operations (Create, Read, Update, Delete)           │
│  └─ Transaction control                                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│           DOMAIN MODEL (Entities)                           │
│  User, Subject, Syllabus, SyllabusCLO, etc.                 │
│  (SQLAlchemy ORM Models)                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│          DATABASE LAYER (MSSQL)                             │
│  Connection Pool → Session → Database                       │
│                                                               │
│  ├─ Engine (poolclass=QueuePool)                            │
│  ├─ SessionLocal factory                                    │
│  ├─ Session per Request (DI Factory)                        │
│  └─ Transaction isolation                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Issue #1: AiService Double Definition

### Problem Map

```
dependency_container.py (Line ~362)
├─ Definition #1: ai_service = Factory(AiService, audit_repository=...)
│  └─ OVERWRITTEN by...
│
├─ Definition #2: ai_service = Factory(AiService)  ← No audit_repository!
│  └─ Used by all injections
│
└─ Result: ai_service.audit_repository = None (always)
           └─ ai_service._log_usage() fails silently
```

### Impact Chain

```
ai_controller.py
    ↓
ai_service.generate()
    ↓
ai_service._log_usage(...)
    ├─ if self.audit_repository:  ← Always FALSE
    └─ Audit logging NEVER happens
```

### Fix Result

```
dependency_container.py
└─ Single definition with audit_repository properly injected
   └─ ai_service._log_usage() works correctly
      └─ audit_repository.create() called
         └─ AI usage tracked in database ✅
```

---

## Issue #2: Database Session Singleton (CRITICAL)

### Current Problem

```
Request 1                          Request 2
    │                                  │
    ▼                                  ▼
app.py: create_app()             app.py: create_app()
    │                                  │
    ▼                                  ▼
Container()                      Container()
    │                                  │
    └──► db_session = Object(session)  │
         (Global singleton)            │
         └──┐                          │
            │                          │
            ▼                          ▼
       SHARED SESSION ◄────────────────┘
       
       ❌ Race condition!
       ❌ State corruption!
       ❌ Memory leak!
```

### Why It's Critical

```python
# Timeline of corruption:

[TIME 1] Request #1 loads User(id=1, name="Alice")
         session.query(User).get(1)  # user object cached in session
         
[TIME 2] Request #2 modifies the SAME session
         session.query(User).get(1)  # Gets CACHED "Alice" but...
         session.update(User, {1: name="Bob"})  # ...modifies it to "Bob"
         
[TIME 3] Request #1 continues with MODIFIED object
         print(user.name)  # Expected: "Alice", Got: "Bob" 🔥
         
[TIME 4] Request #1 saves its changes
         session.commit()  # Commits Bob's data for Alice's record 🔥🔥🔥
```

### Correct Pattern

```
Request 1                          Request 2
    │                                  │
    ▼                                  ▼
Container.wire()               Container.wire()
    │                                  │
    ├─► db_session = Factory(λ)       │
    │   (Creates NEW session)         │
    │   └──► SessionLocal()           │
    │       └──► New Session #1 ✅    │
    │                                  │
    ▼                                  ▼
syllabus_repository                 syllabus_repository
(session #1)                        (session #2)
    │                                  │
    ▼                                  ▼
Operations isolated          Operations isolated ✅
No shared state              No data corruption ✅
```

---

## Issue #3: Workflow Logic Error

### Current State Machine (BROKEN)

```
                  ┌─────────────────────────────┐
                  │     Application States      │
                  └─────────────────────────────┘
                        │      │      │
                    ┌───┘      │      └───┐
                    ▼          ▼          ▼
                 DRAFT    [PENDING]   APPROVED
                    ▲          │
                    │          │
                    └──────────┘
                   (unclear edge)
                   
                  ❌ "RETURNED" state defined
                     in logic but never set!
```

### Current Code (BROKEN)

```python
def submit_syllabus(self, id: int, user_id: int):
    current_status = (s.status or '').upper()
    
    # Check: Can we submit?
    if current_status not in ('DRAFT', 'REJECTED', 'RETURNED'):  # ← Logic error
        raise ValueError('Cannot submit...')
    
    # But 'RETURNED' is NEVER set anywhere in the code!
    # It's a phantom state that:
    # 1. Never occurs (no code sets it)
    # 2. But is checked for in this function
    # 3. Creating confusion about workflow
```

### Correct State Machine

```
                 ┌─────────────────────────────┐
                 │     Workflow States         │
                 └─────────────────────────────┘
                        │      │      │
            ┌───────────┼──┬───┴─┬────┴───────┐
            ▼           ▼  ▼    ▼            ▼
         DRAFT    ┌─► PENDING ─┐      APPROVED
            ▲     │            │
            │     │            │
            └─────┘ ◄──────────┘
           (rejected)   (approve)
           
           Defined states:
           ✅ DRAFT (initial)
           ✅ PENDING (under review)
           ✅ APPROVED (final)
           ✅ REJECTED (back to DRAFT)
           ❌ RETURNED (remove - phantom state)
```

---

## Issue #4: Missing Authentication on Workflow Operations

### Current Flow (INSECURE)

```
❌ ANYONE can POST /syllabuses/{id}/submit

POST /syllabuses/123/submit
├─ No authentication check
├─ No authorization check
├─ No user identification
└─ Syllabus status: DRAFT → PENDING ✅ (insecure!)

❌ ANYONE can POST /syllabuses/{id}/evaluate

POST /syllabuses/123/evaluate
├─ No authentication check
├─ No role verification (lecturer? coordinator? admin?)
├─ No audit trail of who approved
└─ Syllabus status: PENDING → APPROVED ✅ (insecure!)
```

### Correct Flow (SECURE)

```
✅ AUTHORIZED ONLY can POST /syllabuses/{id}/submit

POST /syllabuses/123/submit
├─ @token_required decorator
│  ├─ Verify JWT token present
│  ├─ Verify token signature
│  ├─ Extract user_id from token
│  └─ Verify user is the lecturer
├─ Only allow if:
│  ├─ user_id matches syllabus.lecturer_id
│  ├─ Current status is DRAFT or REJECTED
│  └─ User has LECTURER role
└─ Log action: who, when, what

✅ COORDINATOR/ADMIN only can POST /syllabuses/{id}/evaluate

POST /syllabuses/123/evaluate
├─ @token_required decorator
├─ Additional @role_required('COORDINATOR')
├─ Verify evaluator has permission
├─ Audit log: evaluator_id, action, timestamp
└─ Prevent lecturer from evaluating own syllabus
```

---

## Issue #5: Error Handling in AI Controller

### Current Flow (BRITTLE)

```
POST /ai/generate
    ↓
data = request.get_json() or {}
subject_name = data.get('subject_name')
    ↓
├─ NO validation if subject_name is empty/null
├─ NO try-catch around service call
├─ NO handling if res is not dict
│
▼
ai_service.generate(subject_name)
    ├─ Call Google Generative AI API
    ├─ 🔥 Can throw: AuthenticationError, RateLimitError, TimeoutError
    │
    ▼ (if exception)
    ├─ Response goes to jsonify() directly
    ├─ Flask crashes with 500 error
    ├─ No error message to client
    └─ Hard to debug

(if success)
    ▼
res = {... JSON from AI ...}
    ├─ Assume it's dict? (NO VERIFICATION)
    │  🔥 Could be: string, number, list, null
    │
    ▼
jsonify(res)  ← Crash if res is not JSON-serializable!
```

### Correct Flow (ROBUST)

```
POST /ai/generate
    ↓
try:
    ├─ Validate input
    │  ├─ Check subject_name exists
    │  ├─ Validate type (string)
    │  └─ Validate length (not too long)
    │
    ├─ Call service
    │  ├─ ai_service.generate(subject_name)
    │
    ├─ Handle expected errors
    │  ├─ except ValidationError: return 422
    │  ├─ except RateLimitError: return 429
    │  ├─ except TimeoutError: return 504
    │  └─ except Exception: return 500 with message
    │
    ├─ Validate response
    │  ├─ if not isinstance(res, dict): return 500
    │  ├─ if 'error' in res: return 400
    │
    └─ Return success
       └─ return jsonify(res), 200

except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return jsonify({'message': 'AI generation failed'}), 500
```

---

## Issue #6: N+1 Query Problem

### Current Implementation (SLOW)

```
create_syllabus(data):
    
    # Validation Phase - 4 SEPARATE QUERIES
    ├─ self.subject_repository.get_by_id(subject_id)      # Query 1
    ├─ self.program_repository.get_by_id(program_id)      # Query 2
    ├─ self.academic_year_repository.get_by_id(year_id)   # Query 3
    └─ self.user_repository.get_by_id(lecturer_id)        # Query 4
    
    # Header Creation - 1 QUERY
    ├─ self.repository.create(data)                        # Query 5
    
    # Child Creation - 1 + N QUERIES per type
    ├─ for clo in clos_data:
    │  └─ syllabus_clo_repository.create(clo)              # Query 6...N
    ├─ for material in materials_data:
    │  └─ syllabus_material_repository.create(material)    # Query N+1...N+M
    ├─ for plan in teaching_plans:
    │  └─ teaching_plan_repository.create(plan)            # Query N+M+1...N+M+K
    └─ for scheme in schemes_data:
       for component in scheme['components']:
       └─ assessment_component_repository.create(comp)     # Query ...

    EXAMPLE: Create syllabus with:
    ├─ 50 CLOs
    ├─ 30 Materials
    ├─ 15 Teaching Plans
    ├─ 5 Assessment Schemes
    │  └─ 3 Components each (15 total)
    │
    TOTAL: 4 + 1 + 50 + 30 + 15 + 5 + 15 = 120 QUERIES! 🔥
    
    With typical 50ms latency per query:
    └─ 120 × 50ms = 6 SECONDS ❌ (for single request!)
```

### Optimized Implementation

```
create_syllabus(data):
    
    # Validation Phase - 1 OR 4 BATCHED QUERIES
    ├─ Check all FKs with WHERE IN (batch query)
    │  └─ 1-4 queries depending on optimization
    
    # Header Creation - 1 QUERY
    └─ self.repository.create(data)
    
    # Child Creation - BULK INSERT (4 queries instead of N)
    ├─ syllabus_clo_repository.bulk_create(clos_data)      # 1 query (all CLOs)
    ├─ syllabus_material_repository.bulk_create(...)       # 1 query (all materials)
    ├─ teaching_plan_repository.bulk_create(...)           # 1 query (all plans)
    └─ assessment_component_repository.bulk_create(...)    # 1 query (all components)
    
    TOTAL: 4 + 1 + 4 = 9 QUERIES ✅
    
    With same 50ms latency:
    └─ 9 × 50ms = 450ms ✅ (13x faster!)
```

---

## Database Session Lifecycle Comparison

### ❌ CURRENT (Broken)

```
Application Startup
    ↓
dependency_container.py loads
    ├─ from infrastructure.databases.mssql import session
    │
    └─► session = SessionLocal()  # ← Created ONCE here
        └─ Connection opened (held for lifetime of app)
        └─ Object cache allocated
        └─ Identity map created
        └─ Entire app shares this session

Request 1 arrives          Request 2 arrives
    ↓                          ↓
Container.wire()           Container.wire()
    ↓                          ↓
db_session =               db_session =
    providers.Object(       providers.Object(
        session  ◄──────────────┘ SAME SESSION!
    )                      )
    ↓                          ↓
Request 1 gets session     Request 2 gets session
    │                          │
    └──────────┬───────────────┘
               │
               ▼
         SHARED SESSION
         (Race conditions!)
         
         Session state:
         ├─ Current transaction id
         ├─ Object cache
         ├─ Identity map
         ├─ Uncommitted changes
         └─ Foreign key constraints
         
         Both requests modify = CORRUPTION
```

### ✅ CORRECT (Fixed)

```
Application Startup
    ↓
dependency_container.py loads
    ├─ from infrastructure.databases.mssql import SessionLocal, engine
    │
    └─ db_session = providers.Factory(SessionLocal)
       └─ NO session created at startup
       └─ SessionLocal factory stored for later use

Request 1 arrives          Request 2 arrives
    ↓                          ↓
Container wire()           Container wire()
    ↓                          ↓
@inject on route           @inject on route
    │                          │
    ├─ Needs: db_session    ├─ Needs: db_session
    │                          │
    ├─ Calls Factory         ├─ Calls Factory
    │                          │
    ▼                          ▼
SessionLocal()             SessionLocal()
    │                          │
    └─ NEW session ✅       └─ NEW session ✅
       Connection #1           Connection #2
       (from pool)             (from pool)
       
       Session isolated     Session isolated
       
After Request 1            After Request 2
       │                          │
       └─ session.close() ✅  └─ session.close() ✅
          Connection returned to pool
          Memory freed
          No state leakage
```

---

## Security Flow Comparison

### ❌ CURRENT (Insecure)

```
Request: POST /syllabuses/123/submit

┌─────────────────────────────────┐
│ @syllabus_bp.route(...)         │
│ @inject                         │
│ def submit_syllabus(id, service)│
│     # NO @token_required!       │
│     result = service.submit()   │
│     # Who is user? Unknown!     │
│     # What role? Unknown!       │
│     # Audit trail? None!        │
└─────────────────────────────────┘

Anyone can:
✅ POST /syllabuses/1/submit
✅ POST /syllabuses/2/submit
✅ POST /syllabuses/999/submit (even non-existent)

Attack scenarios:
├─ Lecturer submits others' syllabuses
├─ Student approves their own work
├─ Attacker changes workflow state without trace
└─ No audit trail of who did what
```

### ✅ CORRECT (Secure)

```
Request: POST /syllabuses/123/submit
Header: Authorization: Bearer eyJ...

┌─────────────────────────────────────────────┐
│ @token_required  ◄─ Verify & extract token  │
│   ├─ Check token format (Bearer ...)        │
│   ├─ Verify JWT signature                   │
│   ├─ Check expiration                       │
│   ├─ Extract user_id from claims            │
│   └─ Store in g.user_id (Flask context)     │
│                                              │
│ @syllabus_bp.route(...)                     │
│ @inject                                     │
│ def submit_syllabus(id, service):           │
│     user_id = g.user_id  ◄─ Now we know who│
│     if not user_id: 401 Unauthorized        │
│     result = service.submit(id, user_id)    │
│                                              │
│     # Business logic checks:                 │
│     ├─ Is user the lecturer? ✅             │
│     ├─ Is status DRAFT/REJECTED? ✅         │
│     └─ Log action (audit trail) ✅          │
└─────────────────────────────────────────────┘

Protection:
✅ Only authenticated users can access
✅ User identity tied to action
✅ Audit trail: who, when, what
✅ Prevents privilege escalation
```

---

## Summary Relationship Map

```
┌───────────────────────────────────────────────────────────────┐
│                   6 CRITICAL ISSUES                           │
├───────────────────────────────────────────────────────────────┤
│                                                                 │
│ Issue #1 (AiService) ─────► Issue #2 (Session Singleton)     │
│   ├─ Impacts: AI logging           ├─ Impacts: All DB ops    │
│   └─ Data loss risk                └─ Data corruption risk   │
│                                      ├─ Race conditions       │
│ Issue #3 (Workflow Logic)            └─ Memory leaks         │
│   ├─ Impacts: State management                                │
│   ├─ Invalid transitions               Issue #4 (Auth)       │
│   └─ Business rule violations          ├─ Impacts: Access   │
│         ├─ Works with Issue #4         │  control            │
│         └─ Works with Issue #6         └─ Audit trail       │
│                                                                 │
│ Issue #5 (Error Handling) ──► Issue #6 (N+1 Queries)         │
│   ├─ Impacts: Stability               ├─ Impacts: Speed    │
│   ├─ Crashes & 500 errors             ├─ Scalability       │
│   └─ Poor debugging                   └─ Resource usage    │
│                                                                 │
└───────────────────────────────────────────────────────────────┘

Fix Dependency Order:
  1. Issue #2 (Session) - Foundation for everything
  2. Issue #1 (AiService) - Independent fix
  3. Issue #3 (Workflow Logic) - Independent fix
  4. Issue #4 (Auth) - Depends on: Session working
  5. Issue #5 (Error Handling) - Independent fix
  6. Issue #6 (N+1 Queries) - Optimization (lower priority)

Recommended execution:
  Fixes 1,2,3,5 (parallel) → Test → Fix 4 → Test → Fix 6
```

---

**END OF ARCHITECTURE ANALYSIS**
