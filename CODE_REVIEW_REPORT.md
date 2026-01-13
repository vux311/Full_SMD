# 🔍 CODE REVIEW REPORT: Syllabus Management System (SMD)
**Người Review:** Senior Python Backend Developer  
**Ngày Review:** January 13, 2026  
**Phiên Bản:** Clean Architecture + Dependency Injection  

---

## 📊 1. Tóm tắt tình trạng (General Health)

### ✅ Điểm Mạnh
- **Clean Architecture**: Cấu trúc rõ ràng (Controllers → Services → Repositories)
- **Dependency Injection**: Sử dụng `dependency-injector` library đầy đủ
- **DB Session Management**: MSSQL được cấu hình và khởi tạo đúng cách
- **Error Handling**: Middleware xử lý exception toàn bộ app
- **Wiring Configuration**: Danh sách 23 controllers được khai báo trong `Container`

### ⚠️ Vấn Đề Chính
1. **DI Wiring Không Hoàn Toàn**: `AiService` được định nghĩa **2 lần** với config khác nhau
2. **Missing Services**: Không khai báo providers cho một số services quan trọng
3. **Database Session**: Được lưu trực tiếp từ MSSQL module (potential memory leak)
4. **Logic Lỗi**: `SyllabusService.submit_syllabus()` có điều kiện status không rõ ràng
5. **Import Issues**: Một số relative imports có thể fail khi app khởi động

---

## 🚨 2. Các lỗi nghiêm trọng (CRITICAL BUGS) - Cần sửa ngay

### **BUG #1: AiService được định nghĩa 2 lần trong Container** ⚠️ CRITICAL
**File:** [dependency_container.py](dependency_container.py#L362-L370)

**Vấn đề:**
```python
# Dòng ~362
ai_service = providers.Factory(
    AiService,
    audit_repository=ai_auditlog_repository
)

# Dòng ~370 (TRÙNG LẠP!)
from services.ai_service import AiService
ai_service = providers.Factory(
    AiService
)  # ❌ Không inject audit_repository!
```

**Tác động:**
- Phần đầu tiên bị ghi đè bởi phần thứ 2
- `AiService` sẽ không nhận `audit_repository` → `audit_repository=None` luôn
- Logging AI usage không hoạt động

**Sửa lỗi:**
```python
# ❌ XÓA dòng 362-366 (phần đầu tiên)
# ✅ GIỮ LẠI phần này (nhưng bổ sung):

from services.ai_service import AiService
ai_service = providers.Factory(
    AiService,
    audit_repository=ai_auditlog_repository
)
```

---

### **BUG #2: Database Session là instance toàn bộ App** ⚠️ HIGH
**File:** [dependency_container.py](dependency_container.py#L93-L94)  
**File:** [mssql.py](infrastructure/databases/mssql.py)

**Vấn đề:**
```python
# Trong dependency_container.py
from infrastructure.databases.mssql import session  # ← Singleton global
db_session = providers.Object(session)  # ← Tất cả request dùng cùng session

# Trong mssql.py
session = SessionLocal()  # ← Created ONCE at import time
```

**Tác động:**
- Tất cả requests chia sẻ **1 session duy nhất**
- Concurrent requests có thể conflict (data race)
- Session state không được reset giữa requests
- Potential memory leak: entities không được garbage collect

**Sửa lỗi:**
```python
# ✅ Trong dependency_container.py - thay đổi này:
db_session = providers.Factory(
    lambda: SessionLocal(),  # ✅ Tạo session mới cho mỗi Factory call
    # HOẶC:
    # lambda: sessionmaker(autocommit=False, autoflush=False, bind=engine)()
)
```

---

### **BUG #3: Token Decorator không được apply trên cả Service call** ⚠️ MEDIUM
**File:** [syllabus_controller.py](api/controllers/syllabus_controller.py#L147-L160)

**Vấn đề:**
```python
@syllabus_bp.route('/<int:id>/submit', methods=['POST'])
@inject
def submit_syllabus(id: int, ...):  # ← NO @token_required!
    # Submit endpoint có thể gọi bởi unauthenticated user
```

**Tác động:**
- Workflow state changes (DRAFT → PENDING) không được kiểm tra quyền
- Bất kỳ ai cũng có thể submit syllabus của người khác

**Sửa lỗi:**
```python
@syllabus_bp.route('/<int:id>/submit', methods=['POST'])
@token_required  # ✅ THÊM DÒNG NÀY
@inject
def submit_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    ...
```

---

### **BUG #4: SyllabusService.submit_syllabus() có lỗi logic status** ⚠️ HIGH
**File:** [syllabus_service.py](services/syllabus_service.py#L125-L145)

**Vấn đề:**
```python
def submit_syllabus(self, id: int, user_id: int):
    s = self.repository.get_by_id(id)
    if not s:
        return None
    
    current_status = (s.status or '').upper()
    if current_status not in ('DRAFT', 'REJECTED', 'RETURNED'):  # ← Logic sai
         raise ValueError(f'Syllabus cannot be submitted...')
    
    # Status không bao giờ được set là 'RETURNED'
    # Nhưng điều kiện kiểm tra 'RETURNED' - vô lý!
```

**Tác động:**
- Status 'RETURNED' không được define ở đâu
- Điều kiện kiểm tra không rõ ràng
- Workflow state machine bị inconsistent

**Sửa lỗi:**
```python
# ✅ Define workflow states rõ ràng
VALID_SUBMISSION_STATES = ('DRAFT', 'REJECTED')  # Chỉ có 2 state được phép submit

def submit_syllabus(self, id: int, user_id: int):
    s = self.repository.get_by_id(id)
    if not s:
        return None
    
    current_status = (s.status or '').upper()
    if current_status not in VALID_SUBMISSION_STATES:
        raise ValueError(
            f'Cannot submit syllabus in {current_status} status. '
            f'Only {VALID_SUBMISSION_STATES} states allowed.'
        )
    
    from_status = s.status
    updated = self.repository.update(id, {'status': 'PENDING'})
    if self.workflow_log_repository:
        self.workflow_log_repository.create({...})
    return updated
```

---

### **BUG #5: AI Controller không handle exception từ AiService** ⚠️ MEDIUM
**File:** [ai_controller.py](api/controllers/ai_controller.py)

**Vấn đề:**
```python
@ai_bp.route('/generate', methods=['POST'])
@inject
def generate(ai_service: AiService = Provide[Container.ai_service]):
    data = request.get_json() or {}
    subject_name = data.get('subject_name')
    if not subject_name:
        return jsonify({'message': 'subject_name is required'}), 400

    res = ai_service.generate(subject_name)  # ← Có thể throw exception
    if isinstance(res, dict) and res.get('error'):
        return jsonify({'message': res.get('error')}), 500
    
    return jsonify(res), 200  # ← res có thể không là dict
```

**Tác động:**
- Nếu `res` là string hoặc object khác → crash
- Exception từ Google Generative AI không được catch
- Nếu `ai_auditlog_repository.create()` fail → app crash

**Sửa lỗi:**
```python
@ai_bp.route('/generate', methods=['POST'])
@inject
def generate(ai_service: AiService = Provide[Container.ai_service]):
    data = request.get_json() or {}
    subject_name = data.get('subject_name')
    if not subject_name:
        return jsonify({'message': 'subject_name is required'}), 400

    try:
        res = ai_service.generate(subject_name)
        
        # Ensure response is dict
        if not isinstance(res, dict):
            res = {'error': 'Invalid response format from AI service'}
        
        if res.get('error'):
            return jsonify({'message': res.get('error')}), 500
        
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'message': f'AI generation failed: {str(e)}'}), 500
```

---

### **BUG #6: Missing Provider cho StudenService nếu controller gọi** ⚠️ MEDIUM
**File:** [dependency_container.py](dependency_container.py#L340-L345)

**Vấn đề:**
```python
student_service = providers.Factory(
    StudentService, 
    sub_repo=student_subscription_repository,
    report_repo=student_report_repository
)
# ✅ Service được khai báo OK

# NHƯNG: student_controller.py sẽ gọi nó:
# from dependency_injector.wiring import inject, Provide
# @inject
# def some_endpoint(service: StudentService = Provide[Container.student_service]):
```

**Tác Impact:**
- Không critical nếu controller import đúng cách
- Nhưng nếu import từ container trực tiếp → ModuleNotFoundError

**Kiểm tra:** Nếu `student_controller.py` import OK thì không sao.

---

## ⚠️ 3. Các lỗi Logic & Tiềm ẩn (LOGICAL ISSUES)

### **ISSUE #1: SyllabusService.create_syllabus() - N+1 Query Problem**
**File:** [syllabus_service.py](services/syllabus_service.py#L44-L108)

**Vấn đề:**
```python
def create_syllabus(self, data: dict):
    # Validate Foreign Keys - 4 QUERIES
    if not subject_id or not self.subject_repository.get_by_id(subject_id):  # ← 1 query
        raise ValueError('Invalid subject_id')
    if not program_id or not self.program_repository.get_by_id(program_id):  # ← 2 query
        raise ValueError('Invalid program_id')
    if not academic_year_id or not self.academic_year_repository.get_by_id(academic_year_id):  # ← 3 query
        raise ValueError('Invalid academic_year_id')
    if not lecturer_id or not self.user_repository.get_by_id(lecturer_id):  # ← 4 query
        raise ValueError('Invalid lecturer_id')
    
    # Save Header - 1 query
    new_syllabus = self.repository.create(data)
    sid = new_syllabus.id
    
    # Save Children - 1 + N queries
    if self.syllabus_clo_repository:
        for item in clos_data:
            self.syllabus_clo_repository.create(item)  # ← N queries (1 per item)
```

**Impact:** Nếu syllabus có 50 CLOs + 30 Materials + 10 Plans = 91 queries! 📈 Chậm rất nhiều.

**Sửa lỗi:**
```python
# ✅ Validate tất cả FK trong 1 query (hoặc batch)
fk_ids = {
    'subject_id': data.get('subject_id'),
    'program_id': data.get('program_id'),
    'academic_year_id': data.get('academic_year_id'),
    'lecturer_id': data.get('lecturer_id')
}

# Validate batch (1 query per repository type, hoặc dùng WHERE IN)
for fk_type, fk_id in fk_ids.items():
    if not fk_id:
        raise ValueError(f'Missing {fk_type}')

if not self.subject_repository.get_by_id(fk_ids['subject_id']):
    raise ValueError('Invalid subject_id')
# ... (kiểm tra khác)

# ✅ Bulk insert CLOs nếu repository support
if self.syllabus_clo_repository and clos_data:
    for item in clos_data:
        item['syllabus_id'] = sid
    self.syllabus_clo_repository.bulk_create(clos_data)  # ← 1 query instead of N
```

---

### **ISSUE #2: UserRepository.get_by_username() - Potential SQL Injection** ⚠️ MEDIUM
**File:** [user_repository.py](infrastructure/repositories/user_repository.py#L20)

**Hiện tại:**
```python
def get_by_username(self, username: str) -> Optional[User]:
    return self.session.query(User).filter_by(username=username).first()
```

**Tuy nhiên:**
- SQLAlchemy `filter_by()` đã safe từ SQL Injection (parameterized query)
- Nhưng nên thêm `.strip()` để tránh lỗi whitespace

**Sửa lỗi:**
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

### **ISSUE #3: Exception Handling quá generic**
**File:** [app.py](app.py#L53-L58)

**Vấn đề:**
```python
try:
    container.wire(modules=[...])
except Exception:
    pass  # ❌ Silently ignore ALL errors!
```

**Impact:**
- Nếu DI wiring fail → app khởi động nhưng không có services
- Request → NullPointerException ở runtime
- Khó debug

**Sửa lỗi:**
```python
try:
    container.wire(modules=[...])
except Exception as e:
    app.logger.error(f"Failed to wire dependency container: {e}")
    # Either re-raise hoặc log and handle gracefully
    if os.getenv('ENVIRONMENT') == 'production':
        raise  # ✅ In production, fail fast
    else:
        app.logger.warning("Continuing with incomplete DI wiring...")
```

---

### **ISSUE #4: SyllabusSchema không validate nested objects**
**File:** [syllabus_schema.py](api/schemas/syllabus_schema.py) - (cần kiểm tra)

**Tiềm ẩn:**
```python
# Nếu schema định nghĩa như:
class SyllabusSchema(Schema):
    clos = fields.List(fields.Nested(SyllabusCloDtoSchema))
    materials = fields.List(fields.Nested(SyllabusMaterialSchema))
```

**Vấn đề:**
- Nested validation có thể fail nhưng không show error rõ ràng
- Nếu validation fail → trả về error message không help được

**Sửa lỗi:**
```python
# Trong controller validate_and_return
errors = schema.validate(data)
if errors:
    return jsonify({
        'message': 'Validation error',
        'errors': errors  # ✅ Chi tiết lỗi
    }), 422
```

---

### **ISSUE #5: Database connection pool không configured**
**File:** [mssql.py](infrastructure/databases/mssql.py)

**Vấn đề:**
```python
engine = create_engine(DATABASE_URI)
# ❌ Không config connection pool!
# Default pool_size=5, max_overflow=10 có thể không đủ
```

**Sửa lỗi:**
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_size=20,           # ✅ Tăng pool size
    max_overflow=40,        # ✅ Cho phép overflow
    pool_pre_ping=True,     # ✅ Kiểm tra connection trước dùng
    pool_recycle=3600,      # ✅ Recycle connection sau 1 hour
    echo=False              # ✅ Set to True chỉ trong dev mode
)
```

---

## 💡 4. Đề xuất Refactor (Code Tối ưu)

### **REFACTOR #1: Extract Workflow States vào Constants**
**Tạo file mới:** `src/domain/constants.py`

```python
# Workflow States
class WorkflowStatus:
    DRAFT = 'DRAFT'
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    
    VALID_FOR_SUBMISSION = (DRAFT, REJECTED)
    VALID_FOR_EVALUATION = (PENDING,)

# Sử dụng:
from domain.constants import WorkflowStatus

if current_status not in WorkflowStatus.VALID_FOR_SUBMISSION:
    raise ValueError(...)
```

---

### **REFACTOR #2: Implement Unit of Work Pattern**
**Tạo:** `src/infrastructure/repositories/unit_of_work.py`

```python
class UnitOfWork:
    def __init__(self, session):
        self.session = session
        self._repositories = {}
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
    
    def commit(self):
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
    
    def rollback(self):
        self.session.rollback()
```

**Sử dụng:**
```python
def create_syllabus_with_children(data):
    with UnitOfWork(session) as uow:
        new_syllabus = syllabus_repo.create(data)
        
        for clo_data in clos_data:
            clo_data['syllabus_id'] = new_syllabus.id
            clo_repo.create(clo_data)
        
        # Nếu exception → auto rollback
        # Nếu success → auto commit
```

---

### **REFACTOR #3: Add Pagination để tránh quá nhiều data**
**File:** [subject_repository.py](infrastructure/repositories/subject_repository.py)

```python
def get_all(self, page: int = 1, page_size: int = 20) -> dict:
    total = self.session.query(Subject).count()
    items = self.session.query(Subject)\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return {
        'total': total,
        'page': page,
        'page_size': page_size,
        'items': items
    }
```

---

### **REFACTOR #4: Implement Service Decorator cho Transaction**
```python
from functools import wraps

def transactional(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            result = f(self, *args, **kwargs)
            self.repository.session.commit()
            return result
        except Exception as e:
            self.repository.session.rollback()
            raise
    return wrapper

# Sử dụng:
class SyllabusService:
    @transactional
    def create_syllabus(self, data):
        # Auto rollback nếu error
        ...
```

---

### **REFACTOR #5: Add Logging tại mỗi layer**
```python
import logging

logger = logging.getLogger(__name__)

class SyllabusRepository:
    def create(self, data: dict):
        logger.debug(f"Creating syllabus with subject_id={data.get('subject_id')}")
        try:
            result = self.repository.create(data)
            logger.info(f"Syllabus created: id={result.id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create syllabus: {e}", exc_info=True)
            raise
```

---

## ✅ 5. Code sửa lỗi (FULL FIX CODE SNIPPETS)

### **FIX FILE #1: dependency_container.py** (Sửa DI Container)
**Đường dẫn:** `apps/api/src/dependency_container.py`

```python
# Dependency Injection Container

from dependency_injector import containers, providers
from infrastructure.databases.mssql import engine, SessionLocal
from infrastructure.repositories.subject_repository import SubjectRepository
from services.subject_service import SubjectService
# ... (import khác giữ nguyên) ...

class Container(containers.DeclarativeContainer):
    """Dependency Injection Container for SMD services."""

    wiring_config = containers.WiringConfiguration(modules=[
        "api.controllers.subject_controller",
        "api.controllers.faculty_controller",
        # ... (giữ nguyên) ...
    ])

    # ✅ FIX #1: Session Factory (tạo session mới cho mỗi request)
    db_session = providers.Factory(
        lambda: SessionLocal()  # ✅ Tạo session mới thay vì dùng singleton
    )

    # Repositories (giữ nguyên)
    subject_repository = providers.Factory(
        SubjectRepository,
        session=db_session
    )
    
    # ... (các repository khác) ...

    # ✅ FIX #2: Loại bỏ định nghĩa trùng lặp của ai_service
    # Services
    ai_service = providers.Factory(
        AiService,
        api_key=os.getenv('GEMINI_API_KEY'),  # ✅ Inject API key từ env
        audit_repository=ai_auditlog_repository  # ✅ GIỮ LẠI audit_repository
    )
    
    # ✅ Xóa phần này:
    # from services.ai_service import AiService
    # ai_service = providers.Factory(AiService)  # ❌ XÓA!

    # ... (các service khác giữ nguyên) ...
```

---

### **FIX FILE #2: syllabus_service.py** (Sửa logic workflow)
**Đường dẫn:** `apps/api/src/services/syllabus_service.py`

```python
from typing import List, Optional
from infrastructure.repositories.syllabus_repository import SyllabusRepository

# ✅ FIX #1: Define workflow states rõ ràng
class SyllabusWorkflowStatus:
    DRAFT = 'DRAFT'
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

class SyllabusService:
    def __init__(self, repository: SyllabusRepository, ...):
        # ... (giữ nguyên) ...

    def submit_syllabus(self, id: int, user_id: int):
        """✅ FIX #2: Sửa lỗi logic status"""
        s = self.repository.get_by_id(id)
        if not s:
            return None
        
        current_status = (s.status or '').upper()
        
        # ✅ Chỉ cho phép submit từ DRAFT hoặc REJECTED
        valid_states = (SyllabusWorkflowStatus.DRAFT, SyllabusWorkflowStatus.REJECTED)
        if current_status not in valid_states:
            raise ValueError(
                f'Cannot submit syllabus in {current_status} status. '
                f'Valid states for submission: {valid_states}'
            )
        
        from_status = s.status
        updated = self.repository.update(id, {'status': SyllabusWorkflowStatus.PENDING})
        
        if self.workflow_log_repository:
            self.workflow_log_repository.create({
                'syllabus_id': id,
                'actor_id': user_id,
                'action': 'SUBMIT',
                'from_status': from_status,
                'to_status': SyllabusWorkflowStatus.PENDING,
                'comment': None
            })
        return updated

    def evaluate_syllabus(self, id: int, user_id: int, action: str, comment: Optional[str] = None):
        """✅ FIX #3: Better error handling"""
        s = self.repository.get_by_id(id)
        if not s:
            return None
        
        action = action.upper()
        if action not in ('APPROVE', 'REJECT'):
            raise ValueError(f'Invalid action: {action}. Must be APPROVE or REJECT')
        
        # ✅ Check current status
        if s.status != SyllabusWorkflowStatus.PENDING:
            raise ValueError(
                f'Can only evaluate PENDING syllabuses. Current status: {s.status}'
            )
        
        from_status = s.status
        
        if action == 'APPROVE':
            new_status = SyllabusWorkflowStatus.APPROVED
        else:  # REJECT
            if not comment:
                raise ValueError('Comment is required when rejecting')
            new_status = SyllabusWorkflowStatus.DRAFT
        
        updated = self.repository.update(id, {'status': new_status})
        
        if self.workflow_log_repository:
            self.workflow_log_repository.create({
                'syllabus_id': id,
                'actor_id': user_id,
                'action': action,
                'from_status': from_status,
                'to_status': new_status,
                'comment': comment
            })
        return updated
```

---

### **FIX FILE #3: ai_controller.py** (Error handling)
**Đường dẫn:** `apps/api/src/api/controllers/ai_controller.py`

```python
from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.ai_service import AiService
import logging

logger = logging.getLogger(__name__)
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/generate', methods=['POST'])
@inject
def generate(ai_service: AiService = Provide[Container.ai_service]):
    """✅ FIX: Add comprehensive error handling"""
    try:
        data = request.get_json() or {}
        subject_name = data.get('subject_name', '').strip()
        
        if not subject_name:
            return jsonify({'message': 'subject_name is required and cannot be empty'}), 400

        logger.info(f"AI generation request for: {subject_name}")
        
        # ✅ Handle service call with proper error handling
        try:
            res = ai_service.generate(subject_name)
        except Exception as e:
            logger.error(f"AI service error: {e}", exc_info=True)
            return jsonify({'message': f'AI service error: {str(e)}'}), 500
        
        # ✅ Validate response type
        if not isinstance(res, dict):
            logger.error(f"Invalid response type from AI service: {type(res)}")
            return jsonify({'message': 'Invalid response from AI service'}), 500
        
        # ✅ Handle error response from AI service
        if res.get('error'):
            error_msg = res.get('error')
            logger.warning(f"AI generation error: {error_msg}")
            return jsonify({'message': error_msg}), 400
        
        logger.info(f"AI generation successful for: {subject_name}")
        return jsonify(res), 200
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'message': str(e)}), 422
    except Exception as e:
        logger.error(f"Unexpected error in /ai/generate: {e}", exc_info=True)
        return jsonify({'message': 'Unexpected error occurred'}), 500
```

---

### **FIX FILE #4: mssql.py** (Database configuration)
**Đường dẫn:** `apps/api/src/infrastructure/databases/mssql.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from config import Config
from infrastructure.databases.base import Base

# Database configuration
DATABASE_URI = Config.DATABASE_URI

# ✅ FIX: Proper connection pool configuration
engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_size=20,              # ✅ Connection pool size
    max_overflow=40,           # ✅ Additional connections beyond pool_size
    pool_pre_ping=True,        # ✅ Verify connection before use
    pool_recycle=3600,         # ✅ Recycle connection after 1 hour
    echo=Config.DEBUG,         # ✅ Log SQL queries in debug mode
    connect_args={
        'timeout': 30,
        'check_same_thread': False  # ✅ For SQLite, if used
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False      # ✅ Don't expire objects after commit
)

def init_mssql(app):
    """✅ FIX: Initialize database with proper error handling"""
    try:
        Base.metadata.create_all(bind=engine)
        app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Failed to create database tables: {e}")
        raise

# ✅ NOTE: Session cần được tạo PER REQUEST, không global!
# Trong dependency_container.py: db_session = providers.Factory(SessionLocal)
```

---

### **FIX FILE #5: app.py** (Error handling và logging)**
**Đường dẫn:** `apps/api/src/app.py`

```python
from flask import Flask, jsonify
from api.swagger import spec
from api.middleware import middleware
from infrastructure.databases import init_db
from flasgger import Swagger
from flask_swagger_ui import get_swaggerui_blueprint
from cors import init_cors
import logging
import os

# Dependency injection
from dependency_container import Container
from api.controllers.subject_controller import subject_bp
# ... (import blueprints) ...

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Initialize CORS early so Swagger and other blueprints respect it
    try:
        init_cors(app)
        logger.info("CORS initialized")
    except Exception as e:
        logger.warning(f"CORS initialization warning: {e}")

    Swagger(app)

    # Initialize DI container and wire controllers
    container = Container()
    
    # ✅ FIX: Proper error handling for DI wiring
    try:
        container.wire(modules=[
            "api.controllers.subject_controller",
            "api.controllers.faculty_controller",
            # ... (list all controllers) ...
        ])
        logger.info("Dependency injection wiring successful")
    except Exception as e:
        error_msg = f"Failed to wire dependency container: {e}"
        logger.error(error_msg, exc_info=True)
        
        # ✅ In production, fail fast; in development, allow partial wiring
        if os.getenv('ENVIRONMENT', 'development') == 'production':
            raise RuntimeError(error_msg)
        else:
            logger.warning("Continuing with incomplete DI wiring in development mode")

    # Register blueprints
    app.register_blueprint(subject_bp)
    app.register_blueprint(faculty_bp)
    # ... (register all blueprints) ...

    # Swagger UI
    SWAGGER_URL = '/docs'
    API_URL = '/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Syllabus Management API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Database
    try:
        init_db(app)
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        if os.getenv('ENVIRONMENT') == 'production':
            raise

    # Middleware
    middleware(app)
    logger.info("Middleware initialized")

    return app
```

---

### **FIX FILE #6: syllabus_controller.py** (Add token_required)**
**Đường dẫn:** `apps/api/src/api/controllers/syllabus_controller.py`

```python
from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.syllabus_service import SyllabusService
from api.schemas.syllabus_schema import SyllabusSchema
from api.schemas.syllabus_detail_schema import SyllabusDetailSchema
from api.middleware import token_required

syllabus_bp = Blueprint('syllabus', __name__, url_prefix='/syllabuses')

# ... (existing code) ...

@syllabus_bp.route('/<int:id>/submit', methods=['POST'])
@token_required  # ✅ ADD THIS - Require authentication
@inject
def submit_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """✅ FIX: Require authentication for workflow action"""
    try:
        # Get user_id from token (passed by @token_required decorator)
        from flask import g
        user_id = getattr(g, 'user_id', None)
        
        if not user_id:
            return jsonify({'message': 'User not authenticated'}), 401
        
        result = syllabus_service.submit_syllabus(id, user_id)
        
        if not result:
            return jsonify({'message': 'Syllabus not found'}), 404
        
        return jsonify({'message': 'Syllabus submitted successfully', 'data': schema.dump(result)}), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 422
    except Exception as e:
        return jsonify({'message': 'Error submitting syllabus'}), 500


@syllabus_bp.route('/<int:id>/evaluate', methods=['POST'])
@token_required  # ✅ ADD THIS
@inject
def evaluate_syllabus(id: int, syllabus_service: SyllabusService = Provide[Container.syllabus_service]):
    """✅ FIX: Require authentication for evaluation"""
    try:
        from flask import g
        user_id = getattr(g, 'user_id', None)
        
        if not user_id:
            return jsonify({'message': 'User not authenticated'}), 401
        
        data = request.get_json() or {}
        action = data.get('action')
        comment = data.get('comment')
        
        if not action:
            return jsonify({'message': 'action is required'}), 422
        
        result = syllabus_service.evaluate_syllabus(id, user_id, action, comment)
        
        if not result:
            return jsonify({'message': 'Syllabus not found'}), 404
        
        return jsonify({'message': 'Evaluation completed', 'data': schema.dump(result)}), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 422
    except Exception as e:
        return jsonify({'message': 'Error evaluating syllabus'}), 500
```

---

## 🎯 6. Action Plan (Thứ tự ưu tiên)

| Ưu tiên | Lỗi | File | Severity | Thời gian | Người chịu trách nhiệm |
|---------|------|------|----------|----------|----------------------|
| 🔴 CRITICAL | AiService định nghĩa 2 lần | dependency_container.py | CRITICAL | 15 min | Backend Lead |
| 🔴 CRITICAL | Database session singleton | dependency_container.py, mssql.py | CRITICAL | 30 min | Backend Lead |
| 🟠 HIGH | SyllabusService.submit_syllabus() logic error | syllabus_service.py | HIGH | 20 min | Developer |
| 🟠 HIGH | Missing @token_required | syllabus_controller.py | HIGH | 10 min | Developer |
| 🟡 MEDIUM | AI Controller error handling | ai_controller.py | MEDIUM | 25 min | Developer |
| 🟡 MEDIUM | Connection pool config | mssql.py | MEDIUM | 15 min | Backend Lead |
| 🟢 LOW | Generic exception handling | app.py | LOW | 20 min | Developer |
| 🟢 LOW | N+1 query problem | syllabus_service.py | LOW | 1 hour | Developer |

---

## 📝 Ghi chú cuối cùng

1. **Test trước khi deploy**: Chạy integration test sau khi áp dụng fixes
2. **Database migration**: Nếu có change DB schema, cần migration
3. **API documentation**: Update Swagger docs sau khi change endpoints
4. **Performance testing**: Test với 1000+ syllabuses để kiểm tra N+1 query issue
5. **Load testing**: Kiểm tra connection pool với concurrent requests

---

**Review Date:** 2026-01-13  
**Reviewer:** Senior Python Backend Developer  
**Status:** ✅ COMPLETED
