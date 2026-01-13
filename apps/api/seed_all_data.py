import sys
import os
import json
from datetime import datetime, date
from werkzeug.security import generate_password_hash

# --- CẤU HÌNH ĐƯỜNG DẪN IMPORT ---
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# --- IMPORT MODULES ---
try:
    from infrastructure.databases.mssql import session, engine, Base
    from infrastructure.models import (
        User, Role, UserRole, Faculty, Department, Program, ProgramOutcome,
        Subject, AcademicYear, Syllabus, SyllabusClo, SyllabusMaterial,
        TeachingPlan, AssessmentScheme, AssessmentComponent, Rubric,
        CloPloMapping, AssessmentClo, SubjectRelationship,
        SystemSetting, StudentSubscription, StudentReport, Notification
    )
except ImportError as e:
    print(f"❌ Lỗi Import: {e}")
    sys.exit(1)

# ----------------------------------------

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def seed_all():
    print("🌱 Bắt đầu nạp dữ liệu mẫu (Full Enterprise Version)...")
    
    # 1. Reset Database (Optional - cẩn thận khi dùng trên Prod)
    # Base.metadata.drop_all(bind=engine)
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Đã kiểm tra/tạo bảng Database.")
    except Exception as e:
        print(f"⚠️ Cảnh báo tạo bảng: {e}")

    try:
        # ==========================================
        # PHẦN 1: HỆ THỐNG & CẤU HÌNH
        # ==========================================
        print("🔹 1. Seeding System Settings...")
        settings = [
            ("PASSING_GRADE", "4.0", "FLOAT", "Điểm sàn qua môn"),
            ("MAX_FILE_SIZE", "10", "INT", "Kích thước file tối đa (MB)"),
            ("CURRENT_TERM", "HK1_2025", "STRING", "Học kỳ hiện tại"),
            ("ALLOW_STUDENT_COMMENT", "True", "BOOLEAN", "Cho phép sinh viên bình luận"),
            ("AI_MODEL_VERSION", "gemini-2.5-flash", "STRING", "Model AI mặc định")
        ]
        for key, val, type_, desc in settings:
            if not session.query(SystemSetting).filter_by(key=key).first():
                session.add(SystemSetting(key=key, value=val, type=type_, description=desc))
        session.flush()

        # ==========================================
        # PHẦN 2: TỔ CHỨC & NGƯỜI DÙNG
        # ==========================================
        print("🔹 2. Seeding Roles, Faculties, Departments, Users...")
        
        # Roles
        roles_data = ["Admin", "Lecturer", "Head of Dept", "Academic Affairs", "Student", "Dean"]
        role_objs = {}
        for r_name in roles_data:
            role = session.query(Role).filter_by(name=r_name).first()
            if not role:
                role = Role(name=r_name, description=f"Vai trò {r_name}")
                session.add(role)
            role_objs[r_name] = role
        session.flush()

        # Faculty
        fit = session.query(Faculty).filter_by(code="FIT").first()
        if not fit:
            fit = Faculty(code="FIT", name="Công nghệ Thông tin")
            session.add(fit)
            session.flush()

        # Departments
        depts = [
            ("SE", "Kỹ thuật Phần mềm"),
            ("CS", "Khoa học Máy tính"),
            ("IS", "Hệ thống Thông tin")
        ]
        dept_objs = {}
        for code, name in depts:
            d = session.query(Department).filter_by(code=code).first()
            if not d:
                d = Department(code=code, name=name, faculty_id=fit.id)
                session.add(d)
            dept_objs[code] = d
        session.flush()

        # Users
        users_config = [
            # Username, Name, Role, Dept Code
            ("admin", "Super Admin", "Admin", None),
            ("gv_se", "Nguyễn Văn A (GV)", "Lecturer", "SE"),
            ("gv_cs", "Trần Thị B (GV)", "Lecturer", "CS"),
            ("hod_se", "TS. Lê Văn C (Trưởng BM)", "Head of Dept", "SE"),
            ("aa_user", "Phòng Đào Tạo", "Academic Affairs", None),
            ("sv_hcmut", "Nguyễn Sinh Viên", "Student", "SE"),
        ]
        
        user_map = {}
        default_pass = hash_password("123456")

        for uname, fullname, rname, dcode in users_config:
            u = session.query(User).filter_by(username=uname).first()
            dept_id = dept_objs[dcode].id if dcode else None
            
            if not u:
                u = User(
                    username=uname, email=f"{uname}@hcmut.edu.vn",
                    full_name=fullname, password_hash=default_pass,
                    department_id=dept_id, is_active=True
                )
                session.add(u)
                session.flush()
                # Assign Role
                session.add(UserRole(user_id=u.id, role_id=role_objs[rname].id))
            user_map[uname] = u
        session.flush()

        # ==========================================
        # PHẦN 3: CẤU TRÚC ĐÀO TẠO (MASTER DATA)
        # ==========================================
        print("🔹 3. Seeding Academic Master Data...")

        # Academic Year
        ay = session.query(AcademicYear).filter_by(code="2025-2026").first()
        if not ay:
            ay = AcademicYear(code="2025-2026", start_date=date(2025,9,1), end_date=date(2026,6,30))
            session.add(ay)
            session.flush()

        # Program (CTĐT)
        prog = session.query(Program).filter_by(name="Kỹ sư PM K2025").first()
        if not prog:
            prog = Program(department_id=dept_objs["SE"].id, name="Kỹ sư PM K2025", total_credits=150)
            session.add(prog)
            session.flush()

        # Program Outcomes (PLOs)
        plo_objs = []
        existing_plos = session.query(ProgramOutcome).filter_by(program_id=prog.id).count()
        if existing_plos == 0:
            plos_data = [
                ("PLO1", "Áp dụng kiến thức toán học, khoa học và kỹ thuật"),
                ("PLO2", "Thiết kế và hiện thực hóa giải pháp phần mềm"),
                ("PLO3", "Kỹ năng giao tiếp và làm việc nhóm"),
                ("PLO4", "Nhận thức về đạo đức nghề nghiệp"),
                ("PLO5", "Khả năng học tập suốt đời")
            ]
            for c, d in plos_data:
                p = ProgramOutcome(program_id=prog.id, code=c, description=d)
                session.add(p)
                plo_objs.append(p)
            session.flush()
        else:
            plo_objs = session.query(ProgramOutcome).filter_by(program_id=prog.id).all()

        # Subjects
        subjects_data = [
            ("IT001", "Nhập môn Lập trình", 3),
            ("SE104", "Nhập môn CNPM", 3),
            ("SE301", "Kiểm thử phần mềm", 3),
            ("SE401", "Đồ án chuyên ngành", 2)
        ]
        subj_map = {}
        for code, name, cr in subjects_data:
            s = session.query(Subject).filter_by(code=code).first()
            if not s:
                s = Subject(
                    department_id=dept_objs["SE"].id,
                    code=code, name_vi=name, name_en=name + " (En)",
                    credits=cr, credit_theory=cr, credit_practice=0, credit_self_study=cr*2
                )
                session.add(s)
            subj_map[code] = s
        session.flush()

        # Subject Relationships (Môn tiên quyết)
        # IT001 -> SE104
        rel = session.query(SubjectRelationship).filter_by(subject_id=subj_map["SE104"].id, related_subject_id=subj_map["IT001"].id).first()
        if not rel:
            session.add(SubjectRelationship(
                subject_id=subj_map["SE104"].id, 
                related_subject_id=subj_map["IT001"].id, 
                type="PREREQUISITE"
            ))

        # ==========================================
        # PHẦN 4: ĐỀ CƯƠNG CHI TIẾT (SYLLABUS FULL)
        # ==========================================
        print("🔹 4. Seeding Full Syllabus (Header + Children)...")
        
        # Tạo Syllabus cho môn SE104
        target_sub = subj_map["SE104"]
        lecturer = user_map["gv_se"]
        
        syl = session.query(Syllabus).filter_by(subject_id=target_sub.id, version="2.0").first()
        if not syl:
            syl = Syllabus(
                subject_id=target_sub.id,
                program_id=prog.id,
                academic_year_id=ay.id,
                lecturer_id=lecturer.id,
                status="APPROVED", # Đã duyệt để SV thấy
                version="2.0",
                time_allocation=json.dumps({"theory": 30, "practice": 15, "self_study": 90}),
                prerequisites="IT001 - Nhập môn lập trình",
                publish_date=datetime.now(),
                is_active=True
            )
            session.add(syl)
            session.flush()

            # 4.1 Syllabus CLOs
            clo1 = SyllabusClo(syllabus_id=syl.id, code="CLO1", description="Hiểu các quy trình phát triển phần mềm (Waterfall, Agile)")
            clo2 = SyllabusClo(syllabus_id=syl.id, code="CLO2", description="Vận dụng kỹ thuật lấy yêu cầu và phân tích")
            clo3 = SyllabusClo(syllabus_id=syl.id, code="CLO3", description="Thiết kế kiến trúc hệ thống cơ bản")
            session.add_all([clo1, clo2, clo3])
            session.flush()

            # 4.2 CLO-PLO Mapping
            # Map CLO1 -> PLO1 (I), CLO2 -> PLO2 (R), CLO3 -> PLO2 (M)
            if len(plo_objs) >= 2:
                session.add(CloPloMapping(syllabus_clo_id=clo1.id, program_plo_id=plo_objs[0].id, level="I"))
                session.add(CloPloMapping(syllabus_clo_id=clo2.id, program_plo_id=plo_objs[1].id, level="R"))
                session.add(CloPloMapping(syllabus_clo_id=clo3.id, program_plo_id=plo_objs[1].id, level="M"))

            # 4.3 Materials
            mat1 = SyllabusMaterial(syllabus_id=syl.id, type="MAIN", title="Software Engineering (10th Edition)", author="Ian Sommerville")
            mat2 = SyllabusMaterial(syllabus_id=syl.id, type="REFERENCE", title="Clean Code", author="Robert C. Martin")
            session.add_all([mat1, mat2])

            # 4.4 Teaching Plan
            plans = [
                TeachingPlan(syllabus_id=syl.id, week=1, topic="Tổng quan CNPM", activity="Giảng lý thuyết", assessment="Điểm danh"),
                TeachingPlan(syllabus_id=syl.id, week=2, topic="Quy trình phần mềm", activity="Thảo luận nhóm", assessment="Quiz 1"),
                TeachingPlan(syllabus_id=syl.id, week=3, topic="Thu thập yêu cầu", activity="Thực hành Lab", assessment="Bài tập 1"),
            ]
            session.add_all(plans)

            # 4.5 Assessment Scheme -> Component -> Rubric
            # Scheme: Quá trình (50%)
            scheme1 = AssessmentScheme(syllabus_id=syl.id, name="Đánh giá quá trình", weight=50)
            session.add(scheme1)
            session.flush()

            comp1 = AssessmentComponent(scheme_id=scheme1.id, name="Đồ án nhóm", weight=30)
            comp2 = AssessmentComponent(scheme_id=scheme1.id, name="Kiểm tra trắc nghiệm", weight=20)
            session.add_all([comp1, comp2])
            session.flush()

            # Mapping Assessment -> CLO
            # Đồ án nhóm đánh giá CLO2 và CLO3
            session.add(AssessmentClo(assessment_component_id=comp1.id, syllabus_clo_id=clo2.id))
            session.add(AssessmentClo(assessment_component_id=comp1.id, syllabus_clo_id=clo3.id))
            
            # Rubric cho Đồ án nhóm
            rubric1 = Rubric(component_id=comp1.id, criteria="Tài liệu SRS", max_score=5, description_level_pass="Đầy đủ use case", description_level_fail="Thiếu diagram")
            rubric2 = Rubric(component_id=comp1.id, criteria="Thiết kế DB", max_score=5, description_level_pass="Chuẩn hóa 3NF", description_level_fail="Sai quan hệ")
            session.add_all([rubric1, rubric2])

            # Scheme: Cuối kỳ (50%)
            scheme2 = AssessmentScheme(syllabus_id=syl.id, name="Thi cuối kỳ", weight=50)
            session.add(scheme2)
            session.flush()
            
            comp3 = AssessmentComponent(scheme_id=scheme2.id, name="Bài thi tự luận", weight=50)
            session.add(comp3)
            session.flush()
            # Thi cuối kỳ đánh giá hết
            session.add(AssessmentClo(assessment_component_id=comp3.id, syllabus_clo_id=clo1.id))
            session.add(AssessmentClo(assessment_component_id=comp3.id, syllabus_clo_id=clo2.id))
            session.add(AssessmentClo(assessment_component_id=comp3.id, syllabus_clo_id=clo3.id))

        # ==========================================
        # PHẦN 5: TÍNH NĂNG SINH VIÊN & THÔNG BÁO
        # ==========================================
        print("🔹 5. Seeding Student Features & Notifications...")
        
        student = user_map["sv_hcmut"]
        
        # Student Subscription (SV đăng ký theo dõi môn SE104)
        sub = session.query(StudentSubscription).filter_by(student_id=student.id, subject_id=subj_map["SE104"].id).first()
        if not sub:
            session.add(StudentSubscription(student_id=student.id, subject_id=subj_map["SE104"].id))

        # Student Report (SV báo lỗi đề cương)
        # Chỉ tạo nếu syllabus đã tồn tại
        if syl:
            rep = session.query(StudentReport).filter_by(student_id=student.id, syllabus_id=syl.id).first()
            if not rep:
                session.add(StudentReport(
                    student_id=student.id, 
                    syllabus_id=syl.id, 
                    content="Mục tài liệu tham khảo link bị hỏng ạ.",
                    status="PENDING"
                ))

        # Notification (Thông báo cho GV)
        note = session.query(Notification).filter_by(user_id=lecturer.id, title="Hệ thống đã sẵn sàng").first()
        if not note:
            session.add(Notification(
                user_id=lecturer.id,
                title="Hệ thống đã sẵn sàng",
                message="Chào mừng bạn đến với hệ thống quản lý đề cương v2.0",
                type="SYSTEM",
                is_read=False
            ))

        session.commit()
        print("\n✅✅✅ SEEDING HOÀN TẤT THÀNH CÔNG! (ALL SYSTEMS GO) ✅✅✅")
        print(f"👉 Admin: admin / 123456")
        print(f"👉 Lecturer: gv_se / 123456")
        print(f"👉 Student: sv_hcmut / 123456")

    except Exception as e:
        session.rollback()
        print(f"\n❌ CÓ LỖI XẢY RA: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    seed_all()