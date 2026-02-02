"""
Script to reset database and seed comprehensive test data
Usage: python reset_and_seed.py
"""

import sys
import os
from datetime import datetime, timedelta
import json
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.databases.mssql import engine, SessionLocal
# --- Models ---
from infrastructure.models.user_model import User
from infrastructure.models.role_model import Role
from infrastructure.models.user_role_model import UserRole
from infrastructure.models.department_model import Department
from infrastructure.models.subject_model import Subject
from infrastructure.models.subject_relationship_model import SubjectRelationship
from infrastructure.models.program_model import Program
from infrastructure.models.program_outcome_model import ProgramOutcome # <--- Mới
from infrastructure.models.academic_year_model import AcademicYear
from infrastructure.models.syllabus_model import Syllabus
from infrastructure.models.syllabus_clo_model import SyllabusClo
from infrastructure.models.clo_plo_mapping_model import CloPloMapping
from infrastructure.models.assessment_clo_model import AssessmentClo
from infrastructure.models.syllabus_material_model import SyllabusMaterial
from infrastructure.models.teaching_plan_model import TeachingPlan
from infrastructure.models.assessment_scheme_model import AssessmentScheme
from infrastructure.models.assessment_component_model import AssessmentComponent
from infrastructure.models.rubric_model import Rubric
from infrastructure.models.notification_model import Notification
from infrastructure.models.syllabus_snapshot_model import SyllabusSnapshot
from infrastructure.models.system_setting_model import SystemSetting
from infrastructure.models.workflow_log_model import WorkflowLog
from infrastructure.models.faculty_model import Faculty
from infrastructure.models.syllabus_current_workflow import SyllabusCurrentWorkflow
from infrastructure.models.syllabus_comment_model import SyllabusComment
from infrastructure.models.workflow_state_model import WorkflowState
from infrastructure.models.workflow_transition_model import WorkflowTransition
from infrastructure.models.ai_auditlog_model import AiAuditLog
from infrastructure.models.system_auditlog_model import SystemAuditLog
from infrastructure.models.student_report_model import StudentReport
from infrastructure.models.student_subscription_model import StudentSubscription
from infrastructure.models.notification_template_model import NotificationTemplate
from infrastructure.databases.base import Base
from domain.constants import WorkflowStatus
from werkzeug.security import generate_password_hash

def reset_database(session):
    """Drop and recreate all tables"""
    print("🗑️  Resetting database...")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("   ✓ Dropped all tables")
    
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    print("   ✓ Created all tables")

def seed_roles(session):
    """Create roles"""
    print("\n👥 Seeding roles...")
    
    roles_data = [
        {"name": "Admin", "description": "System Administrator"},
        {"name": "Lecturer", "description": "University Lecturer"},
        {"name": "Student", "description": "University Student"},
        {"name": "Head of Dept", "description": "Head of Department"},
        {"name": "Academic Affairs", "description": "Academic Affairs Office"},
        {"name": "Principal", "description": "University Principal / Final Approver"},
    ]
    
    roles = []
    for r in roles_data:
        role = Role(**r)
        session.add(role)
        roles.append(role)
    
    session.commit()
    print(f"   ✓ Created {len(roles)} roles")
    return {r.name: r for r in roles}

def seed_users(session, roles_dict):
    """Create users with various roles"""
    print("\n👤 Seeding users...")
    
    users_data = [
        # Admin
        {"username": "admin", "email": "admin@university.edu", "full_name": "System Admin", "role": "Admin"},
        
        # Principal
        {"username": "principal1", "email": "principal@university.edu", "full_name": "GS.TS. Hiệu Trưởng", "role": "Principal"},
        
        # Lecturers
        {"username": "lecturer1", "email": "nguyen.van.a@university.edu", "full_name": "Nguyễn Văn A", "role": "Lecturer"},
        {"username": "lecturer2", "email": "tran.thi.b@university.edu", "full_name": "Trần Thị B", "role": "Lecturer"},
        {"username": "lecturer3", "email": "le.van.c@university.edu", "full_name": "Lê Văn C", "role": "Lecturer"},
        {"username": "lecturer4", "email": "pham.thi.d@university.edu", "full_name": "Phạm Thị D", "role": "Lecturer"},
        {"username": "lecturer5", "email": "hoang.van.e@university.edu", "full_name": "Hoàng Văn E", "role": "Lecturer"},
        
        # Head of Department
        {"username": "hod1", "email": "hod.cs@university.edu", "full_name": "Võ Văn Trưởng", "role": "Head of Dept"},
        {"username": "hod2", "email": "hod.se@university.edu", "full_name": "Đỗ Thị Phó", "role": "Head of Dept"},
        
        # Academic Affairs
        {"username": "aa1", "email": "aa1@university.edu", "full_name": "Bùi Văn Học Vụ", "role": "Academic Affairs"},
        {"username": "aa2", "email": "aa2@university.edu", "full_name": "Đinh Thị Đào Tạo", "role": "Academic Affairs"},
        
        # Students
        {"username": "student1", "email": "sv001@student.edu", "full_name": "Nguyễn Minh Tuấn", "role": "Student"},
        {"username": "student2", "email": "sv002@student.edu", "full_name": "Lê Thị Hoa", "role": "Student"},
        {"username": "student3", "email": "sv003@student.edu", "full_name": "Trần Văn Nam", "role": "Student"},
    ]
    
    users = []
    users_by_username = {}
    users_by_role = {}

    for u in users_data:
        role_name = u.pop("role")
        user = User(
            **u,
            password_hash=generate_password_hash("123456"),
            is_active=True
        )
        session.add(user)
        session.flush()
        
        # Assign role
        user_role = UserRole(user_id=user.id, role_id=roles_dict[role_name].id)
        session.add(user_role)
        users.append((user, role_name))

        users_by_username[user.username] = user
        users_by_role.setdefault(role_name, []).append(user)
    
    session.commit()
    print(f"   ✓ Created {len(users)} users (password: 123456)")
    return users_by_username, users_by_role

def seed_faculties(session):
    """Create faculties"""
    print("\n🏛️  Seeding faculties...")
    faculties_data = [
        {"code": "ENG", "name": "Faculty of Engineering", "description": "Engineering and Technology"},
        {"code": "SCI", "name": "Faculty of Science", "description": "Natural Sciences"},
        {"code": "BUS", "name": "Faculty of Business", "description": "Business Administration"},
    ]
    faculties = []
    for f in faculties_data:
        fac = Faculty(**f)
        session.add(fac)
        faculties.append(fac)
    session.commit()
    print(f"   ✓ Created {len(faculties)} faculties")
    return faculties


def seed_departments(session, faculties):
    """Create departments"""
    print("\n🏢 Seeding departments...")
    
    departments_data = [
        {"code": "CS", "name": "Khoa Khoa học Máy tính", "faculty_idx": 0},
        {"code": "SE", "name": "Khoa Công nghệ Phần mềm", "faculty_idx": 0},
        {"code": "IS", "name": "Khoa Hệ thống Thông tin", "faculty_idx": 0},
        {"code": "IT", "name": "Khoa Công nghệ Thông tin", "faculty_idx": 0},
    ]
    
    departments = []
    for d in departments_data:
        faculty_idx = d.pop("faculty_idx")
        faculty_id = faculties[faculty_idx].id if faculties and len(faculties) > faculty_idx else None
        dept = Department(
            faculty_id=faculty_id if faculty_id else None,
            **d
        )
        session.add(dept)
        departments.append(dept)
    
    session.commit()
    print(f"   ✓ Created {len(departments)} departments")
    return departments

def seed_subjects(session, departments):
    """Create subjects"""
    print("\n📚 Seeding subjects...")
    
    subjects_data = [
        # Computer Science
        {"code": "CS101", "name_vi": "Nhập môn Lập trình", "name_en": "Introduction to Programming", "credits": 3, "dept_idx": 0},
        {"code": "CS102", "name_vi": "Cấu trúc Dữ liệu và Giải thuật", "name_en": "Data Structures and Algorithms", "credits": 4, "dept_idx": 0},
        {"code": "CS201", "name_vi": "Cơ sở Dữ liệu", "name_en": "Database Systems", "credits": 3, "dept_idx": 0},
        {"code": "CS202", "name_vi": "Hệ điều hành", "name_en": "Operating Systems", "credits": 3, "dept_idx": 0},
        {"code": "CS301", "name_vi": "Trí tuệ Nhân tạo", "name_en": "Artificial Intelligence", "credits": 4, "dept_idx": 0},
        {"code": "CS302", "name_vi": "Học Máy", "name_en": "Machine Learning", "credits": 4, "dept_idx": 0},
        
        # Software Engineering
        {"code": "SE101", "name_vi": "Nhập môn Công nghệ Phần mềm", "name_en": "Introduction to Software Engineering", "credits": 3, "dept_idx": 1},
        {"code": "SE201", "name_vi": "Phân tích và Thiết kế Hệ thống", "name_en": "System Analysis and Design", "credits": 4, "dept_idx": 1},
        {"code": "SE202", "name_vi": "Kiểm thử Phần mềm", "name_en": "Software Testing", "credits": 3, "dept_idx": 1},
        {"code": "SE301", "name_vi": "Quản lý Dự án Phần mềm", "name_en": "Software Project Management", "credits": 3, "dept_idx": 1},
        
        # Web & Mobile
        {"code": "WEB201", "name_vi": "Lập trình Web", "name_en": "Web Programming", "credits": 4, "dept_idx": 1},
        {"code": "WEB301", "name_vi": "Phát triển Ứng dụng Di động", "name_en": "Mobile Application Development", "credits": 4, "dept_idx": 1},
        
        # Information Systems
        {"code": "IS201", "name_vi": "Hệ thống Thông tin Quản lý", "name_en": "Management Information Systems", "credits": 3, "dept_idx": 2},
        {"code": "IS301", "name_vi": "Phân tích Dữ liệu", "name_en": "Data Analytics", "credits": 4, "dept_idx": 2},
        
        # IT Infrastructure
        {"code": "IT201", "name_vi": "Mạng Máy tính", "name_en": "Computer Networks", "credits": 3, "dept_idx": 3},
        {"code": "IT301", "name_vi": "An toàn và Bảo mật", "name_en": "Security and Network Security", "credits": 4, "dept_idx": 3},
    ]
    
    subjects = []
    for s in subjects_data:
        dept_idx = s.pop("dept_idx")
        subject = Subject(
            department_id=departments[dept_idx].id,
            credit_theory=s["credits"] * 0.6,
            credit_practice=s["credits"] * 0.4,
            **s
        )
        session.add(subject)
        subjects.append(subject)
    
    session.commit()
    print(f"   ✓ Created {len(subjects)} subjects")
    return subjects

def seed_programs(session, departments):
    """Create programs"""
    print("\n🎓 Seeding programs...")
    
    programs_data = [
        {"name": "Computer Science 2020", "dept_idx": 0},
        {"name": "Software Engineering 2021", "dept_idx": 1},
        {"name": "Information Systems 2021", "dept_idx": 2},
        {"name": "Information Technology 2022", "dept_idx": 3},
    ]
    
    programs = []
    for p in programs_data:
        dept_idx = p.pop("dept_idx")
        program = Program(
            department_id=departments[dept_idx].id,
            total_credits=120,
            name=p.get("name")
        )
        session.add(program)
        programs.append(program)
    
    session.commit()
    print(f"   ✓ Created {len(programs)} programs")
    return programs

# --- NEW: Function to seed PLOs ---
def seed_plos(session, programs):
    """Create PLOs for each program"""
    print("\n🎯 Seeding Program Learning Outcomes (PLOs)...")
    
    plos_created = 0
    for program in programs:
        # Create 5-8 PLOs per program
        for i in range(1, 8):
            plo = ProgramOutcome(
                program_id=program.id,
                code=f"PLO{i}",
                description=f"Sinh viên có khả năng vận dụng kiến thức (PLO {i} của {program.name})"
            )
            session.add(plo)
            plos_created += 1
    
    session.commit()
    print(f"   ✓ Created {plos_created} PLOs")
# ----------------------------------

def seed_academic_years(session):
    """Create academic years"""
    print("\n📅 Seeding academic years...")
    
    current_year = datetime.now().year
    years_data = [
        {"code": f"{current_year-2}-{current_year-1}", "is_active": False},
        {"code": f"{current_year-1}-{current_year}", "is_active": False},
        {"code": f"{current_year}-{current_year+1}", "is_active": True},
        {"code": f"{current_year+1}-{current_year+2}", "is_active": False},
    ]
    
    years = []
    for y in years_data:
        year = AcademicYear(**y)
        session.add(year)
        years.append(year)
    
    session.commit()
    print(f"   ✓ Created {len(years)} academic years")
    return years

def seed_subject_relationships(session, subjects):
    """Create relationship between subjects"""
    print("\n🔗 Seeding subject relationships...")
    
    # Example: MATH101 is prerequisite for IT101
    math101 = next((s for s in subjects if s.code == 'MATH101'), None)
    it101 = next((s for s in subjects if s.code == 'IT101'), None)
    
    # IT101 is prerequisite for IT102
    it102 = next((s for s in subjects if s.code == 'IT102'), None)
    
    # ENG101 is parallel for IT101
    eng101 = next((s for s in subjects if s.code == 'ENG101'), None)
    
    rels = []
    if math101 and it101:
        rels.append(SubjectRelationship(subject_id=it101.id, related_subject_id=math101.id, type='PREREQUISITE'))
    if it101 and it102:
        rels.append(SubjectRelationship(subject_id=it102.id, related_subject_id=it101.id, type='PREREQUISITE'))
    if eng101 and it101:
        rels.append(SubjectRelationship(subject_id=it101.id, related_subject_id=eng101.id, type='PARALLEL'))
        
    for r in rels:
        session.add(r)
    
    session.commit()
    print(f"   ✓ Seeded {len(rels)} subject relationships")
    return rels

def seed_syllabuses(session, subjects, programs, years, users_by_username, users_by_role):
    """Create syllabuses with full children and 5-step workflow state"""
    print("\n📝 Seeding syllabuses (5-step workflow)...")
    
    lecturers = users_by_role.get("Lecturer", [])
    hods = users_by_role.get("Head of Dept", [])
    aas = users_by_role.get("Academic Affairs", [])
    principals = users_by_role.get("Principal", [])
    
    # Fallback to admin if specific roles missing
    admin = users_by_username.get("admin")
    if not lecturers: lecturers = [admin]
    if not hods: hods = [admin]
    if not aas: aas = [admin]
    if not principals: principals = [admin]

    # Use the 5-step workflow statuses from domain.constants
    statuses = [
        WorkflowStatus.DRAFT, 
        WorkflowStatus.PENDING_REVIEW, 
        WorkflowStatus.PENDING_APPROVAL, 
        WorkflowStatus.APPROVED, 
        WorkflowStatus.PUBLISHED, 
        WorkflowStatus.RETURNED,
        WorkflowStatus.REJECTED
    ]
    
    syllabuses_created = 0
    clos_created = 0
    mappings_created = 0
    materials_created = 0
    plans_created = 0
    assessment_schemes_created = 0
    components_created = 0
    assessment_clos_created = 0
    rubrics_created = 0
    comments_created = 0
    snapshots_created = 0
    
    for idx, subject in enumerate(subjects[:15]):
        # Distribute statuses across subjects
        status = statuses[idx % len(statuses)]
        lecturer_user = lecturers[idx % len(lecturers)]
        hod_user = hods[idx % len(hods)]
        aa_user = aas[idx % len(aas)]
        principal_user = principals[idx % len(principals)]
        
        program = programs[idx % len(programs)]
        year = years[2] # Current active year

        # More realistic time allocation
        time_alloc = {
            "theory": 30,
            "exercises": 10,
            "practice": 15,
            "selfStudy": 90
        }

        # Create syllabus
        syllabus = Syllabus(
            subject_id=subject.id,
            program_id=program.id,
            academic_year_id=year.id,
            lecturer_id=lecturer_user.id,
            head_department_id=hod_user.id,
            dean_id=principal_user.id,
            status=status,
            version="1.0",
            time_allocation=json.dumps(time_alloc),
            prerequisites=f"Điều kiện: Hoàn thành {subject.credits} tín chỉ" if idx > 3 else "Không có điều kiện tiên quyết",
            description=f"Học phần {subject.name_vi} cung cấp kiến thức nền tảng và chuyên sâu về {subject.name_en}.",
            objectives=json.dumps([f"Hiểu rõ kiến thức cốt lõi của {subject.name_vi}", "Áp dụng kỹ năng giải quyết vấn đề thực tế"]),
            student_duties="Tham gia 80% thời gian lên lớp, hoàn thành bài tập tuần.",
            other_requirements="Laptop cá nhân cài đặt các công cụ lập trình.",
            pre_courses=subjects[max(0, idx-2)].code if idx > 2 else "",
            co_courses="",
            course_type="Bắt buộc" if idx < 10 else "Tự chọn",
            component_type="Cơ sở ngành" if idx < 7 else "Chuyên ngành",
            date_prepared=(datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
            date_edited=datetime.now().strftime("%Y-%m-%d"),
            head_department=hod_user.full_name,
            dean=principal_user.full_name,
            is_active=(status in [WorkflowStatus.PUBLISHED, WorkflowStatus.APPROVED]),
            publish_date=datetime.now() if status == WorkflowStatus.PUBLISHED else None,
            created_at=datetime.now() - timedelta(days=60),
            updated_at=datetime.now()
        )
        session.add(syllabus)
        session.flush()
        syllabuses_created += 1
        
        # Add Active Workflow tracking record if it's in progress
        if status in [WorkflowStatus.PENDING_REVIEW, WorkflowStatus.PENDING_APPROVAL, WorkflowStatus.APPROVED]:
            assigned_user_id = hod_user.id
            if status == WorkflowStatus.PENDING_APPROVAL: assigned_user_id = aa_user.id
            elif status == WorkflowStatus.APPROVED: assigned_user_id = principal_user.id
            
            cw = SyllabusCurrentWorkflow(
                syllabus_id=syllabus.id,
                state=status,
                assigned_user_id=assigned_user_id,
                last_action_at=datetime.now() - timedelta(days=random.randint(1, 5))
            )
            session.add(cw)

        # Add CLOs
        num_clos = 4
        current_clos = []
        for i in range(num_clos):
            clo = SyllabusClo(
                syllabus_id=syllabus.id,
                code=f"CLO{i+1}",
                description=f"Sinh viên có khả năng {['phân tích', 'thiết kế', 'triển khai', 'tổng hợp'][i % 4]} các module của {subject.code}."
            )
            session.add(clo)
            current_clos.append(clo)
            clos_created += 1
        session.flush()

        # Seed MAPPINGS (CLO -> PLO)
        program_plos = session.query(ProgramOutcome).filter_by(program_id=program.id).all()
        if program_plos:
            for clo in current_clos:
                selected_plos = random.sample(program_plos, k=min(len(program_plos), 2))
                for plo in selected_plos:
                    mapping = CloPloMapping(
                        syllabus_clo_id=clo.id,
                        program_plo_id=plo.id,
                        level=random.choice(['I', 'R', 'M'])
                    )
                    session.add(mapping)
                    mappings_created += 1

        # Assessment Schemes
        scheme = AssessmentScheme(syllabus_id=syllabus.id, name="Đánh giá học phần", weight=100.0)
        session.add(scheme)
        session.flush()
        assessment_schemes_created += 1

        # Assessment Components
        comp_configs = [
            {"name": "Điểm quá trình", "weight": 20, "method": "Chuyên cần & Bài tập", "criteria": "Tham gia lớp và làm bài tập tuần"},
            {"name": "Kiểm tra giữa kỳ", "weight": 30, "method": "Tự luận", "criteria": "Hiểu kiến thức từ tuần 1-8"},
            {"name": "Thi cuối kỳ", "weight": 50, "method": "Đồ án", "criteria": "Sản phẩm thực tế & Báo cáo"}
        ]
        curr_components = []
        for config in comp_configs:
            comp = AssessmentComponent(
                scheme_id=scheme.id, 
                name=config["name"], 
                weight=config["weight"],
                method=config["method"],
                criteria=config["criteria"]
            )
            session.add(comp)
            curr_components.append(comp)
            components_created += 1
        session.flush()

        # Link Components to CLOs (AssessmentClo)
        for comp in curr_components:
            # Each component covers 1-2 CLOs
            comp_clos = random.sample(current_clos, k=random.randint(1, 2))
            for clo in comp_clos:
                session.add(AssessmentClo(assessment_component_id=comp.id, syllabus_clo_id=clo.id))
                assessment_clos_created += 1
            
            # Add Rubrics for Project component
            if "Đồ án" in str(comp.method):
                rubrics_data = [
                    {"crit": "Giao diện và trải nghiệm người dùng", "max": 3.0, "pass": "Giao diện sạch sẽ, dễ dùng", "fail": "Giao diện lỗi, khó dùng"},
                    {"crit": "Chức năng hệ thống", "max": 5.0, "pass": "Đầy đủ các chức năng yêu cầu", "fail": "Thiếu nhiều hơn 2 chức năng"},
                    {"crit": "Báo cáo và thuyết trình", "max": 2.0, "pass": "Trình bày mạch lạc, báo cáo đúng định dạng", "fail": "Không chuẩn bị kỹ"}
                ]
                for r_data in rubrics_data:
                    session.add(Rubric(
                        component_id=comp.id,
                        criteria=r_data["crit"],
                        max_score=r_data["max"],
                        description_level_pass=r_data["pass"],
                        description_level_fail=r_data["fail"]
                    ))
                    rubrics_created += 1

        # Add Comments for returned/rejected syllabuses
        if status in [WorkflowStatus.RETURNED, WorkflowStatus.REJECTED]:
            session.add(SyllabusComment(
                syllabus_id=syllabus.id,
                user_id=hod_user.id if status == WorkflowStatus.RETURNED else aa_user.id,
                content=f"Nội dung chuẩn đầu ra {current_clos[0].code} cần được viết lại rõ ràng hơn, tránh các động từ mơ hồ như 'Hiểu', nên dùng 'Phân tích' hoặc 'Thiết kế'.",
                is_resolved=False
            ))
            comments_created += 1
        
        # Add Materials
        materials = [
            {"type": "Main", "title": f"Giáo trình {subject.name_vi}"},
            {"type": "Ref", "title": f"Tài liệu tham khảo {subject.name_en}"},
        ]
        for mat in materials:
            session.add(SyllabusMaterial(syllabus_id=syllabus.id, type=mat["type"], title=mat["title"]))
            materials_created += 1
        
        # Add Teaching Plans (15 weeks)
        for week in range(1, 16):
            target_clo = current_clos[(week-1) % num_clos]
            session.add(TeachingPlan(
                syllabus_id=syllabus.id,
                week=week,
                topic=f"Tuần {week}: {['Lý thuyết tổng quan', 'Phân tích yêu cầu', 'Thiết kế hệ thống', 'Triển khai mã nguồn', 'Tối ưu hóa'][week % 5]}",
                activity=f"Giảng bài & {['Thảo luận nhóm', 'Làm lab', 'Kiểm tra nhanh'][week % 3]}",
                assessment=f"Gắn với chuẩn {target_clo.code}" if week % 2 == 0 else ""
            ))
            plans_created += 1

        # Workflow Logs
        if status != WorkflowStatus.DRAFT:
            session.add(WorkflowLog(
                syllabus_id=syllabus.id,
                actor_id=lecturer_user.id,
                action="SUBMIT",
                from_status=WorkflowStatus.DRAFT,
                to_status=WorkflowStatus.PENDING_REVIEW,
                comment="Nộp bản thảo đề cương mới."
            ))
            
        if status in [WorkflowStatus.PUBLISHED, WorkflowStatus.APPROVED]:
            snapshot = SyllabusSnapshot(
                syllabus_id=syllabus.id,
                version="1.0",
                snapshot_data={"info": f"Finalized snapshot for {subject.code}"},
                created_by=lecturer_user.id
            )
            session.add(snapshot)
            snapshots_created += 1

    session.commit()
    print(f"   ✓ Created {syllabuses_created} syllabuses with 5-step states")
    print(f"   ✓ Created {clos_created} CLOs")
    print(f"   ✓ Created {mappings_created} CLO-PLO Mappings")
    print(f"   ✓ Created {assessment_clos_created} Assessment-CLO Links")
    print(f"   ✓ Created {rubrics_created} Rubrics")
    print(f"   ✓ Created {comments_created} Comments")
    print(f"   ✓ Created {materials_created} materials")
    print(f"   ✓ Created {plans_created} teaching plans")

def seed_system_settings(session):
    """Seed initial system settings"""
    print("\n⚙️ Seeding system settings...")
    settings = [
        {"key": "UNIVERSITY_NAME", "value": "Đại học Công nghệ Quốc gia", "data_type": "STRING", "description": "Tên trường hiển thị trên đề cương"},
        {"key": "UNIVERSITY_WEBSITE", "value": "https://unq.edu.vn", "data_type": "STRING", "description": "Website chính thức của nhà trường"},
        {"key": "UNIVERSITY_LOGO_URL", "value": "https://unq.edu.vn/logo.png", "data_type": "STRING", "description": "Đường dẫn đến logo của trường"},
        {"key": "workflow_deadline_days", "value": "5", "data_type": "NUMBER", "description": "Hạn chót phê duyệt mặc định (ngày) cho mỗi bước trong quy trình"},
        {"key": "current_academic_year", "value": "2025-2026", "data_type": "STRING", "description": "Năm học hiện hành của hệ thống"},
        {"key": "enable_email_notifications", "value": "true", "data_type": "BOOLEAN", "description": "Bật/Tắt hệ thống gửi thông báo qua email"},
    ]
    for s in settings:
        session.add(SystemSetting(**s))
    session.commit()
    print(f"   ✓ Created {len(settings)} system settings")

def main():
    """Main execution"""
    print("="*60)
    print("🚀 SYLLABUS MANAGEMENT SYSTEM - DATA RESET & SEED")
    print("="*60)
    
    session = SessionLocal()
    
    try:
        # Reset database
        reset_database(session)
        
        # Seed data
        roles_dict = seed_roles(session)
        users_by_username, users_by_role = seed_users(session, roles_dict)
        faculties = seed_faculties(session)
        departments = seed_departments(session, faculties)
        subjects = seed_subjects(session, departments)
        seed_subject_relationships(session, subjects)
        programs = seed_programs(session, departments)
        
        # --- CALL NEW PLO SEEDER ---
        seed_plos(session, programs) 
        # ---------------------------
        
        years = seed_academic_years(session)
        seed_system_settings(session)
        seed_syllabuses(session, subjects, programs, years, users_by_username, users_by_role)
        
        print("\n" + "="*60)
        print("✅ DATABASE RESET AND SEED COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n🔑 Login credentials:")
        print("   • Admin: admin / 123456")
        print("   • Lecturer: lecturer1 / 123456")
        print("   • Student: student1 / 123456")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()