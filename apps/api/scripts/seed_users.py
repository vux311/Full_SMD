from dependency_container import Container
from datetime import date


def get_or_create(service, list_method_name, check_attr, check_value, create_method_name, create_data):
    list_method = getattr(service, list_method_name)
    for item in list_method():
        if getattr(item, check_attr) == check_value:
            return item
    create_method = getattr(service, create_method_name)
    return create_method(create_data)


def seed():
    container = Container()

    # Services
    role_service = container.role_service()
    user_service = container.user_service()
    faculty_service = container.faculty_service()
    department_service = container.department_service()
    academic_year_service = container.academic_year_service()
    program_service = container.program_service()
    subject_service = container.subject_service()
    syllabus_service = container.syllabus_service()
    syllabus_clo_service = container.syllabus_clo_service()
    syllabus_material_service = container.syllabus_material_service()

    # 1) Roles
    admin_role = role_service.get_by_name('ADMIN') or role_service.create_role({'name': 'ADMIN', 'description': 'ADMIN role'})
    print('✅  Role:', admin_role.name)
    lecturer_role = role_service.get_by_name('LECTURER') or role_service.create_role({'name': 'LECTURER', 'description': 'LECTURER role'})
    print('✅  Role:', lecturer_role.name)

    # 2) Users
    admin = user_service.get_by_username('admin')
    if not admin:
        admin = user_service.create_user({'username': 'admin', 'email': 'admin@example.com', 'full_name': 'Admin User', 'password': 'password123', 'is_active': True})
        print('✅  Created User: admin')
    else:
        print('✅  Found User: admin')

    lecturer = user_service.get_by_username('lecturer')
    if not lecturer:
        lecturer = user_service.create_user({'username': 'lecturer', 'email': 'lecturer@example.com', 'full_name': 'Lecturer User', 'password': 'password123', 'is_active': True})
        print('✅  Created User: lecturer')
    else:
        print('✅  Found User: lecturer')

    # Assign roles idempotently
    session = container.db_session()
    from infrastructure.models.user_role_model import UserRole

    def ensure_role(user, role):
        if not session.query(UserRole).filter_by(user_id=user.id, role_id=role.id).first():
            try:
                session.add(UserRole(user_id=user.id, role_id=role.id))
                session.commit()
                print(f"✅  Assigned role {role.name} to user {user.username}")
            except Exception:
                session.rollback()

    ensure_role(admin, admin_role)
    ensure_role(lecturer, lecturer_role)

    # 3) Faculty & Department
    faculty = get_or_create(faculty_service, 'list_faculties', 'code', 'FIT', 'create_faculty', {'code': 'FIT', 'name': 'Faculty of Information Technology'})
    print(f"✅  Faculty: {faculty.code} - {faculty.name}")

    department = None
    # department needs faculty_id
    for d in department_service.list_departments():
        if d.code == 'SE' and d.faculty_id == faculty.id:
            department = d
            break
    if not department:
        department = department_service.create_department({'faculty_id': faculty.id, 'code': 'SE', 'name': 'Software Engineering'})
        print('✅  Created Department: SE')
    else:
        print('✅  Found Department: SE')

    # 4) Academic Year, Program, Subject
    academic_year = get_or_create(academic_year_service, 'list_academic_years', 'code', '2025-2026', 'create_academic_year', {'code': '2025-2026', 'start_date': date(2025,9,1), 'end_date': date(2026,6,30)})
    print(f"✅  AcademicYear: {academic_year.code}")

    program = get_or_create(program_service, 'list_programs', 'name', 'Software Engineering K18', 'create_program', {'department_id': department.id, 'name': 'Software Engineering K18', 'total_credits': 120})
    print(f"✅  Program: {program.name}")

    subject = None
    for s in subject_service.list_subjects():
        if s.code == 'SWT301' and s.department_id == department.id:
            subject = s
            break
    if not subject:
        subject = subject_service.create_subject({'department_id': department.id, 'code': 'SWT301', 'name_vi': 'Giới thiệu Kỹ thuật Phần mềm', 'name_en': 'Introduction to Software Engineering', 'credits': 3})
        print('✅  Created Subject: SWT301')
    else:
        print('✅  Found Subject: SWT301')

    # 5) Syllabus
    syllabus = None
    for sy in syllabus_service.list_syllabuses():
        if sy.subject_id == subject.id and sy.program_id == program.id and sy.academic_year_id == academic_year.id:
            syllabus = sy
            break
    if not syllabus:
        syllabus = syllabus_service.create_syllabus({'subject_id': subject.id, 'program_id': program.id, 'academic_year_id': academic_year.id, 'lecturer_id': lecturer.id, 'version': '1.0'})
        print(f"✅  Created Syllabus ID: {syllabus.id}")
    else:
        print(f"✅  Found Syllabus ID: {syllabus.id}")

    # 6) Syllabus Details - CLOs
    existing_clos = {c.code for c in syllabus_clo_service.get_by_syllabus(syllabus.id)}
    clos_to_add = [
        {'code': 'CLO1', 'description': 'Explain software lifecycle.'},
        {'code': 'CLO2', 'description': 'Apply software requirements engineering.'},
        {'code': 'CLO3', 'description': 'Design basic software architecture.'},
    ]
    for clo in clos_to_add:
        if clo['code'] not in existing_clos:
            item = syllabus_clo_service.create_clo({'syllabus_id': syllabus.id, **clo})
            print(f"✅  Added CLO: {item.code}")
        else:
            print(f"✅  CLO exists: {clo['code']}")

    # Materials
    existing_mats = {m.title for m in syllabus_material_service.get_by_syllabus(syllabus.id)}
    mats_to_add = [
        {'type': 'MAIN', 'title': 'Software Engineering (Textbook)', 'author': 'Ian Sommerville', 'publisher': 'Pearson', 'isbn': '1234567890', 'syllabus_id': syllabus.id},
        {'type': 'REFERENCE', 'title': 'Design Patterns', 'author': 'Gamma et al.', 'publisher': 'Addison-Wesley', 'isbn': '0987654321', 'syllabus_id': syllabus.id},
    ]
    for mat in mats_to_add:
        if mat['title'] not in existing_mats:
            item = syllabus_material_service.create_material(mat)
            print(f"✅  Added Material: {item.title}")
        else:
            print(f"✅  Material exists: {mat['title']}")

    # Teaching Plans
    teaching_plan_service = container.teaching_plan_service()
    existing_weeks = {p.week for p in teaching_plan_service.list_plans_for_syllabus(syllabus.id)}
    plans_to_add = [
        {'week': 1, 'topic': 'Introduction to Software Engineering', 'activity': 'Lecture', 'assessment': 'Quiz', 'syllabus_id': syllabus.id},
        {'week': 2, 'topic': 'Software Process Models', 'activity': 'Lecture', 'assessment': 'Assignment 1', 'syllabus_id': syllabus.id},
        {'week': 3, 'topic': 'Requirements Engineering', 'activity': 'Lecture', 'assessment': 'Assignment 2', 'syllabus_id': syllabus.id},
    ]
    for plan in plans_to_add:
        if plan['week'] not in existing_weeks:
            item = teaching_plan_service.create_teaching_plan(plan)
            print(f"✅  Added Teaching Plan Week: {item.week}")
        else:
            print(f"✅  Teaching Plan exists for week: {plan['week']}")

    # Assessments: Schemes, Components, Rubrics, CLO mappings
    assessment_scheme_service = container.assessment_scheme_service()
    assessment_component_service = container.assessment_component_service()
    rubric_service = container.rubric_service()
    assessment_clo_service = container.assessment_clo_service()

    existing_schemes = {s.name for s in assessment_scheme_service.list_schemes_for_syllabus(syllabus.id)}

    # Example scheme: Midterm
    if 'Midterm' not in existing_schemes:
        scheme = assessment_scheme_service.create_scheme({'syllabus_id': syllabus.id, 'name': 'Midterm', 'weight': 30.0})
        print(f"✅  Created Assessment Scheme: {scheme.name}")
        comp = assessment_component_service.create_component({'scheme_id': scheme.id, 'name': 'Midterm Exam', 'weight': 30.0})
        print(f"✅  Created Assessment Component: {comp.name}")
        rubric = rubric_service.create_rubric({'component_id': comp.id, 'criteria': 'Comprehensive exam', 'max_score': 100})
        print(f"✅  Created Rubric for component: {rubric.criteria}")
        # Map to CLO1 if exists
        clo1 = None
        for c in syllabus_clo_service.get_by_syllabus(syllabus.id):
            if c.code == 'CLO1':
                clo1 = c
                break
        if clo1:
            assessment_clo_service.add_mapping(comp.id, clo1.id)
            print(f"✅  Mapped component {comp.name} to CLO {clo1.code}")
    else:
        print('✅  Midterm scheme exists')

    print('\n✅  Seeding complete!')


if __name__ == '__main__':
    seed()
