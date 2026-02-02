import json
import os
from datetime import datetime, timedelta

file_path = r'c:\Users\songh\SMD-Project\apps\api\src\scripts\reset_and_seed.py'
content = open(file_path, encoding='utf-8').read()

start_marker = 'def seed_syllabuses(session, subjects, programs, years, users_by_username, users_by_role):'
end_marker = 'def seed_system_settings(session):'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_func = """def seed_syllabuses(session, subjects, programs, years, users_by_username, users_by_role):
    \"\"\"Create syllabuses with full children and 5-step workflow state\"\"\"
    print("\\n📝 Seeding syllabuses (5-step workflow)...")
    
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
            description=f"Học phần {subject.name_vi} ({subject.code}) cung cấp cho sinh viên kiến thức căn bản về {subject.name_en}. "
                        f"Nội dung bao gồm các mô hình lý thuyết, kỹ năng thực hành và ứng dụng trong thực tiễn.",
            objectives=json.dumps([
                f"Nắm vững các khái niệm cơ bản của {subject.name_vi}.",
                f"Có khả năng thiết kế và triển khai các hệ thống liên quan đến {subject.name_en}.",
                "Phát triển kỹ năng làm việc nhóm và giải quyết vấn đề kỹ thuật."
            ]),
            student_duties="1. Tham dự tối thiểu 80% số tiết học trên lớp.\\n2. Hoàn thành tất cả bài tập về nhà và bài tập lớn.\\n3. Tham gia đầy đủ các buổi thi giữa kỳ và cuối kỳ.",
            other_requirements="Sinh viên cần có laptop cá nhân với cấu hình tối thiểu để chạy các công cụ mô phỏng.",
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
                last_action_at=datetime.now() - timedelta(days=5)
            )
            session.add(cw)

        # Add CLOs
        num_clos = 4
        current_clos = []
        for i in range(num_clos):
            clo = SyllabusClo(
                syllabus_id=syllabus.id,
                code=f"CLO{i+1}",
                description=f"Sinh viên có khả năng {['phân tích', 'thiết kế', 'triển khai', 'đánh giá', 'tổng hợp'][i % 4]} các module của {subject.code}."
            )
            session.add(clo)
            current_clos.append(clo)
            clos_created += 1
        session.flush()

        # Seed MAPPINGS (CLO -> PLO)
        program_plos = session.query(ProgramOutcome).filter_by(program_id=program.id).all()
        if program_plos:
            for clo in current_clos:
                import random
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
        scheme = AssessmentScheme(syllabus_id=syllabus.id, name="Đánh giá học phần chuẩn", weight=100.0)
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
            import random
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
                for r_item in rubrics_data:
                    session.add(Rubric(
                        component_id=comp.id,
                        criteria=r_item["crit"],
                        max_score=r_item["max"],
                        description_level_pass=r_item["pass"],
                        description_level_fail=r_item["fail"]
                    ))
                    rubrics_created += 1

        # Add Comments
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
            {"type": "Main", "title": f"Giáo trình chính: {subject.name_vi} (Nhà xuất bản Đại học)"},
            {"type": "Ref", "title": f"Tài liệu nâng cao: Advanced {subject.name_en} (Tác giả quốc tế)"},
            {"type": "Ref", "title": f"Trang web tài liệu: {subject.code}-docs.com"},
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

"""
    new_content = content[:start_idx] + new_func + content[end_idx:]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS")
else:
    print(f"NOT FOUND: {start_idx}, {end_idx}")
