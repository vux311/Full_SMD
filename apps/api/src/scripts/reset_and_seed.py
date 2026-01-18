"""
Script to reset database and seed comprehensive test data
Usage: python reset_and_seed.py
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.databases.mssql import engine, SessionLocal
from infrastructure.models.user_model import User
from infrastructure.models.role_model import Role
from infrastructure.models.user_role_model import UserRole
from infrastructure.models.department_model import Department
from infrastructure.models.subject_model import Subject
from infrastructure.models.subject_relationship_model import SubjectRelationship
from infrastructure.models.program_model import Program
from infrastructure.models.academic_year_model import AcademicYear
from infrastructure.models.syllabus_model import Syllabus
from infrastructure.models.syllabus_clo_model import SyllabusClo
from infrastructure.models.syllabus_material_model import SyllabusMaterial
from infrastructure.models.teaching_plan_model import TeachingPlan
from infrastructure.models.assessment_scheme_model import AssessmentScheme
from infrastructure.models.assessment_component_model import AssessmentComponent
from infrastructure.models.rubric_model import Rubric
from infrastructure.models.notification_model import Notification
from infrastructure.models.syllabus_snapshot_model import SyllabusSnapshot
from infrastructure.models.system_setting_model import SystemSetting
from infrastructure.models.workflow_log_model import WorkflowLog
from infrastructure.databases.base import Base
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
    """Create users with various roles

    Returns:
        users_by_username: dict username -> User
        users_by_role: dict role_name -> list[User]
    """
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

from infrastructure.models.faculty_model import Faculty

def seed_faculties(session):
    """Create faculties"""
    print("\n🏛️ Seeding faculties...")
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
        # In current DB schema Faculty model may not be implemented; set faculty_id to NULL if none
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
    """Create syllabuses with full children"""
    print("\n📝 Seeding syllabuses...")
    
    lecturers = users_by_role.get("Lecturer", [])
    # Fallback to any user if no lecturers exist
    if not lecturers:
        print("   ⚠️ No lecturers found in seed data, falling back to first available user.")
        all_users = list(users_by_username.values())
        if not all_users:
            raise RuntimeError("No users available to assign as lecturers.")
        lecturers = [all_users[0]]

    statuses = ["Draft", "Draft", "Pending", "Approved", "Approved", "Returned"]  # More approved for testing
    
    syllabuses_created = 0
    clos_created = 0
    materials_created = 0
    plans_created = 0
    assessment_schemes_created = 0
    components_created = 0
    snapshots_created = 0
    
    # Create syllabuses for each subject (some have multiple versions)
    for idx, subject in enumerate(subjects[:12]):  # First 12 subjects
        # Determine how many versions for this subject
        num_versions = 1 if idx < 6 else 2  # Some subjects have 2 versions
        
        for version_idx in range(num_versions):
            version = f"1.{version_idx}"
            status = statuses[syllabuses_created % len(statuses)]
            lecturer_user = lecturers[syllabuses_created % len(lecturers)]
            program = programs[syllabuses_created % len(programs)]
            year = years[1 if version_idx == 0 else 2]  # Old version vs new version
            
            # Create syllabus
            syllabus = Syllabus(
                subject_id=subject.id,
                program_id=program.id,
                academic_year_id=year.id,
                lecturer_id=lecturer_user.id,
                status=status,
                version=version,
                time_allocation=json.dumps({"theory": 30, "exercises": 10, "practice": 20, "selfStudy": 15}),
                prerequisites=f"Điều kiện: Hoàn thành {subject.credits} tín chỉ" if idx > 3 else "Không có điều kiện tiên quyết",
                description=f"Học phần {subject.name_vi} cung cấp kiến thức nền tảng về {subject.name_en.lower()}. "
                           f"Sinh viên sẽ được trang bị kỹ năng thực hành qua các bài tập và dự án thực tế. "
                           f"Môn học gồm {subject.credits} tín chỉ với phương pháp giảng dạy kết hợp lý thuyết và thực hành.",
                objectives=json.dumps([
                    f"Hiểu rõ các khái niệm cơ bản về {subject.name_vi}",
                    f"Áp dụng kiến thức vào giải quyết vấn đề thực tế",
                    f"Phát triển kỹ năng làm việc nhóm và thuyết trình",
                ]),
                student_duties="Tham gia đầy đủ các buổi học, hoàn thành bài tập và dự án đúng hạn, chủ động tìm kiếm tài liệu học tập.",
                other_requirements="Sinh viên cần có laptop cá nhân và cài đặt các công cụ lập trình cần thiết.",
                pre_courses=subjects[max(0, idx-2)].code if idx > 1 else "",
                co_courses=subjects[min(len(subjects)-1, idx+1)].code if idx < len(subjects)-1 else "",
                course_type="Bắt buộc" if idx < 8 else "Tự chọn",
                component_type="Cơ sở ngành" if idx < 5 else "Chuyên ngành",
                date_prepared=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                date_edited=datetime.now().strftime("%Y-%m-%d"),
                dean="PGS.TS. Nguyễn Văn Trưởng",
                head_department="TS. Trần Thị Phó",
                is_active=True,
                created_at=datetime.now() - timedelta(days=60),
                updated_at=datetime.now()
            )
            session.add(syllabus)
            session.flush()
            syllabuses_created += 1
            
            # Add CLOs (3-5 CLOs per syllabus)
            num_clos = 3 + (syllabuses_created % 3)
            current_clos = []
            for i in range(num_clos):
                clo = SyllabusClo(
                    syllabus_id=syllabus.id,
                    code=f"CLO{i+1}",
                    description=f"Sinh viên có khả năng {['phân tích', 'thiết kế', 'triển khai', 'đánh giá', 'tổng hợp'][i % 5]} "
                               f"các vấn đề liên quan đến {subject.name_vi.lower()}."
                )
                session.add(clo)
                current_clos.append(clo)
                clos_created += 1
            session.flush()

            # Add Assessment Schemes
            scheme = AssessmentScheme(
                syllabus_id=syllabus.id,
                name="Ma trận đánh giá chuẩn",
                weight=100.0
            )
            session.add(scheme)
            session.flush()
            assessment_schemes_created += 1

            # Assessment Components (Total weight must be 100)
            components_data = [
                {"name": "Điểm chuyên cần", "weight": 10},
                {"name": "Bài tập lớn / Dự án", "weight": 30},
                {"name": "Thi giữa kỳ", "weight": 20},
                {"name": "Thi cuối kỳ", "weight": 40}
            ]
            for comp_data in components_data:
                comp = AssessmentComponent(
                    scheme_id=scheme.id,
                    name=comp_data["name"],
                    weight=comp_data["weight"]
                )
                session.add(comp)
                components_created += 1
            
            # Add Materials (4-6 materials per syllabus)
            materials = [
                {"type": "Main", "title": f"{subject.name_en} - Textbook Edition {version_idx + 3}, Publisher XYZ"},
                {"type": "Main", "title": f"Lecture Slides - {subject.code} by {lecturer_user.username.upper()}"},
                {"type": "Ref", "title": f"Advanced {subject.name_en} - Reference Guide"},
                {"type": "Ref", "title": f"Online Resources: Coursera, edX, Udemy courses on {subject.name_en}"},
                {"type": "Ref", "title": f"IEEE/ACM Papers on {subject.name_en.split()[0]} Research"},
            ]
            for mat in materials[:4 + (syllabuses_created % 3)]:
                material = SyllabusMaterial(
                    syllabus_id=syllabus.id,
                    type=mat["type"],
                    title=mat["title"]
                )
                session.add(material)
                materials_created += 1
            
            # Add Teaching Plans (12-15 weeks)
            num_weeks = 13 + (syllabuses_created % 3)
            for week in range(1, num_weeks + 1):
                clo_ref = f"CLO{((week-1) % num_clos) + 1}"
                plan = TeachingPlan(
                    syllabus_id=syllabus.id,
                    week=week,
                    topic=f"Tuần {week}: {['Giới thiệu', 'Cơ bản', 'Nâng cao', 'Thực hành', 'Ôn tập'][(week-1) % 5]} - "
                          f"{'Chương ' + str((week-1)//3 + 1) if week <= 12 else 'Thi cuối kỳ'} ({clo_ref})",
                    activity=f"Giảng lý thuyết {2 if week <= 10 else 0} tiết, Thực hành {2 if week <= 10 else 0} tiết, "
                            f"{'Thi giữa kỳ' if week == 7 else 'Thi cuối kỳ' if week == num_weeks else 'Bài tập nhóm'}",
                    assessment="Điểm chuyên cần, Bài tập" if week < num_weeks else "Thi cuối kỳ"
                )
                session.add(plan)
                plans_created += 1

            # Seed Workflow Logs and Snapshots for non-DRAFT
            if status != "Draft":
                # Create a SUBMIT log
                session.add(WorkflowLog(
                    syllabus_id=syllabus.id,
                    actor_id=lecturer_user.id,
                    action="SUBMIT",
                    from_status="Draft",
                    to_status="Pending",
                    comment="Đã hoàn thiện nội dung và gửi duyệt."
                ))
            
            if status in ["Approved", "Published"]:
                # Create Snapshot for approved versions
                snapshot = SyllabusSnapshot(
                    syllabus_id=syllabus.id,
                    version=version,
                    snapshot_data={"info": "Seeded snapshot for testing immutable history"},
                    created_by=users_by_role["Admin"][0].id if users_by_role.get("Admin") else lecturer_user.id
                )
                session.add(snapshot)
                snapshots_created += 1

    session.commit()
    print(f"   ✓ Created {syllabuses_created} syllabuses")
    print(f"   ✓ Created {clos_created} CLOs")
    print(f"   ✓ Created {materials_created} materials")
    print(f"   ✓ Created {plans_created} teaching plans")
    print(f"   ✓ Created {assessment_schemes_created} assessment schemes")
    print(f"   ✓ Created {snapshots_created} snapshots")

def seed_system_settings(session):
    """Seed initial system settings"""
    print("\n⚙️ Seeding system settings...")
    settings = [
        {"key": "UNIVERSITY_NAME", "value": "Đại học Công nghệ Quốc gia", "description": "Tên trường hiển thị trên đề cương"},
        {"key": "ACADEMIC_YEAR_CURRENT", "value": "2025-2026", "description": "Năm học hiện tại mặc định"},
        {"key": "APPROVAL_LEVELS", "value": "3", "description": "Số cấp phê duyệt bắt buộc"},
        {"key": "AI_FEATURES_ENABLED", "value": "true", "description": "Bật/Tắt các tính năng AI hỗ trợ"},
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
        years = seed_academic_years(session)
        seed_system_settings(session)
        seed_syllabuses(session, subjects, programs, years, users_by_username, users_by_role)
        
        print("\n" + "="*60)
        print("✅ DATABASE RESET AND SEED COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   • Roles: {len(roles_dict)}")
        print(f"   • Users: {len(users_by_username)} (Admin: 1, Principal: 1, Lecturers: 5, HOD: 2, AA: 2, Students: 3)")
        print(f"   • Departments: {len(departments)}")
        print(f"   • Subjects: {len(subjects)}")
        print(f"   • Programs: {len(programs)}")
        print(f"   • Academic Years: {len(years)}")
        print(f"   • Syllabuses: {session.query(Syllabus).count()}")
        print(f"   • CLOs, Materials, Teaching Plans: ~500+")
        print("\n🔑 Login credentials:")
        print("   • Admin: admin / 123456")
        print("   • Principal: principal1 / 123456")
        print("   • Lecturer: lecturer1 / 123456")
        print("   • HOD: hod1 / 123456")
        print("   • Academic Affairs: aa1 / 123456")
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
