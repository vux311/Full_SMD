# Dependency Injection Container

from dependency_injector import containers, providers
from infrastructure.databases.mssql import SessionLocal

from infrastructure.repositories.subject_repository import SubjectRepository
from services.subject_service import SubjectService
from infrastructure.repositories.faculty_repository import FacultyRepository
from services.faculty_service import FacultyService
from infrastructure.repositories.department_repository import DepartmentRepository
from services.department_service import DepartmentService
from infrastructure.repositories.role_repository import RoleRepository
from services.role_service import RoleService
from infrastructure.repositories.user_repository import UserRepository
from services.user_service import UserService
from infrastructure.repositories.academic_year_repository import AcademicYearRepository
from services.academic_year_service import AcademicYearService
from infrastructure.repositories.program_repository import ProgramRepository
from services.program_service import ProgramService
from infrastructure.repositories.syllabus_repository import SyllabusRepository
from services.syllabus_service import SyllabusService
from infrastructure.repositories.syllabus_clo_repository import SyllabusCloRepository
from services.syllabus_clo_service import SyllabusCloService
from infrastructure.repositories.syllabus_material_repository import SyllabusMaterialRepository
from services.syllabus_material_service import SyllabusMaterialService
from infrastructure.repositories.teaching_plan_repository import TeachingPlanRepository
from services.teaching_plan_service import TeachingPlanService
from infrastructure.repositories.assessment_scheme_repository import AssessmentSchemeRepository
from services.assessment_scheme_service import AssessmentSchemeService
from infrastructure.repositories.assessment_component_repository import AssessmentComponentRepository
from services.assessment_component_service import AssessmentComponentService
from infrastructure.repositories.rubric_repository import RubricRepository
from services.rubric_service import RubricService
from infrastructure.repositories.assessment_clo_repository import AssessmentCloRepository
from services.assessment_clo_service import AssessmentCloService
from infrastructure.repositories.workflow_log_repository import WorkflowLogRepository

# NEW: Program Outcome, File Management, Mappings, Relationships, Comments, Notifications, System Settings, AI Audit
from infrastructure.repositories.program_outcome_repository import ProgramOutcomeRepository
from services.program_outcome_service import ProgramOutcomeService
from infrastructure.repositories.file_repository import FileRepository
from services.file_service import FileService
from infrastructure.repositories.clo_plo_mapping_repository import CloPloMappingRepository
from services.clo_plo_mapping_service import CloPloMappingService
from infrastructure.repositories.subject_relationship_repository import SubjectRelationshipRepository
from services.subject_relationship_service import SubjectRelationshipService
from infrastructure.repositories.syllabus_comment_repository import SyllabusCommentRepository
from services.syllabus_comment_service import SyllabusCommentService
from infrastructure.repositories.notification_repository import NotificationRepository
from services.notification_service import NotificationService
from infrastructure.repositories.system_setting_repository import SystemSettingRepository
from infrastructure.repositories.ai_auditlog_repository import AiAuditLogRepository
from infrastructure.repositories.notification_repository import NotificationRepository
from infrastructure.repositories.student_subscription_repository import StudentSubscriptionRepository
from infrastructure.repositories.student_report_repository import StudentReportRepository
from services.system_setting_service import SystemSettingService
from services.student_service import StudentService

class Container(containers.DeclarativeContainer):
    """Dependency Injection Container for SMD services."""

    wiring_config = containers.WiringConfiguration(modules=[
        "api.controllers.subject_controller",
        "api.controllers.faculty_controller",
        "api.controllers.department_controller",
        "api.controllers.role_controller",
        "api.controllers.user_controller",
        "api.controllers.academic_year_controller",
        "api.controllers.program_controller",
        "api.controllers.syllabus_controller",
        "api.controllers.syllabus_clo_controller",
        "api.controllers.syllabus_material_controller",
        "api.controllers.teaching_plan_controller",
        "api.controllers.assessment_scheme_controller",
        "api.controllers.assessment_component_controller",
        "api.controllers.rubric_controller",
        "api.controllers.assessment_clo_controller",
        "api.controllers.auth_controller",
        "api.controllers.ai_controller",
        "api.controllers.dashboard_controller",
        "api.controllers.program_outcome_controller",
        "api.controllers.file_controller",
        "api.controllers.clo_plo_mapping_controller",
        "api.controllers.subject_relationship_controller",
        "api.controllers.syllabus_comment_controller",
        "api.controllers.notification_controller",
        "api.controllers.system_setting_controller",
        "api.controllers.student_controller",
    ])

    # Provide a session factory (creates new session per injection)
    from infrastructure.databases.mssql import SessionLocal
    db_session = providers.Factory(SessionLocal)

    # Repositories
    subject_repository = providers.Factory(
        SubjectRepository,
        session=db_session
    )

    faculty_repository = providers.Factory(
        FacultyRepository,
        session=db_session
    )

    department_repository = providers.Factory(
        DepartmentRepository,
        session=db_session
    )

    academic_year_repository = providers.Factory(
        AcademicYearRepository,
        session=db_session
    )

    program_repository = providers.Factory(
        ProgramRepository,
        session=db_session
    )

    role_repository = providers.Factory(
        RoleRepository,
        session=db_session
    )

    user_repository = providers.Factory(
        UserRepository,
        session=db_session
    )
    # Services
    subject_service = providers.Factory(
        SubjectService,
        repository=subject_repository
    )

    faculty_service = providers.Factory(
        FacultyService,
        repository=faculty_repository
    )

    department_service = providers.Factory(
        DepartmentService,
        repository=department_repository
    )

    syllabus_repository = providers.Factory(
        SyllabusRepository,
        session=db_session
    )

    syllabus_clo_repository = providers.Factory(
        SyllabusCloRepository,
        session=db_session
    )

    syllabus_material_repository = providers.Factory(
        SyllabusMaterialRepository,
        session=db_session
    )

    teaching_plan_repository = providers.Factory(
        TeachingPlanRepository,
        session=db_session
    )

    assessment_scheme_repository = providers.Factory(
        AssessmentSchemeRepository,
        session=db_session
    )

    assessment_component_repository = providers.Factory(
        AssessmentComponentRepository,
        session=db_session
    )

    rubric_repository = providers.Factory(
        RubricRepository,
        session=db_session
    )

    assessment_clo_repository = providers.Factory(
        AssessmentCloRepository,
        session=db_session
    )

    workflow_log_repository = providers.Factory(
        WorkflowLogRepository,
        session=db_session
    )

    # NEW REPOSITORIES
    program_outcome_repository = providers.Factory(
        ProgramOutcomeRepository,
        session=db_session
    )
    
    file_repository = providers.Factory(
        FileRepository,
        session=db_session
    )

    clo_plo_mapping_repository = providers.Factory(
        CloPloMappingRepository,
        session=db_session
    )

    subject_relationship_repository = providers.Factory(
        SubjectRelationshipRepository,
        session=db_session
    )

    syllabus_comment_repository = providers.Factory(
        SyllabusCommentRepository,
        session=db_session
    )

    notification_repository = providers.Factory(
        NotificationRepository,
        session=db_session
    )

    system_setting_repository = providers.Factory(
        SystemSettingRepository,
        session=db_session
    )

    student_subscription_repository = providers.Factory(
        StudentSubscriptionRepository,
        session=db_session
    )

    student_report_repository = providers.Factory(
        StudentReportRepository,
        session=db_session
    )

    ai_auditlog_repository = providers.Factory(
        AiAuditLogRepository,
        session=db_session
    )

    academic_year_service = providers.Factory(
        AcademicYearService,
        repository=academic_year_repository
    )

    program_service = providers.Factory(
        ProgramService,
        repository=program_repository
    )

    syllabus_service = providers.Factory(
        SyllabusService,
        repository=syllabus_repository,
        subject_repository=subject_repository,
        program_repository=program_repository,
        academic_year_repository=academic_year_repository,
        user_repository=user_repository,
        workflow_log_repository=workflow_log_repository,
        # NEW INJECTIONS:
        syllabus_clo_repository=syllabus_clo_repository,
        syllabus_material_repository=syllabus_material_repository,
        teaching_plan_repository=teaching_plan_repository,
        assessment_scheme_repository=assessment_scheme_repository,
        assessment_component_repository=assessment_component_repository,
        rubric_repository=rubric_repository,
        assessment_clo_repository=assessment_clo_repository
    )

    syllabus_clo_service = providers.Factory(
        SyllabusCloService,
        repository=syllabus_clo_repository,
        syllabus_repository=syllabus_repository
    )

    syllabus_material_service = providers.Factory(
        SyllabusMaterialService,
        repository=syllabus_material_repository,
        syllabus_repository=syllabus_repository
    )

    teaching_plan_service = providers.Factory(
        TeachingPlanService,
        repository=teaching_plan_repository,
        syllabus_repository=syllabus_repository
    )

    assessment_scheme_service = providers.Factory(
        AssessmentSchemeService,
        repository=assessment_scheme_repository,
        syllabus_repository=syllabus_repository
    )

    assessment_component_service = providers.Factory(
        AssessmentComponentService,
        repository=assessment_component_repository,
        scheme_repository=assessment_scheme_repository
    )

    rubric_service = providers.Factory(
        RubricService,
        repository=rubric_repository,
        component_repository=assessment_component_repository
    )

    assessment_clo_service = providers.Factory(
        AssessmentCloService,
        repository=assessment_clo_repository,
        component_repository=assessment_component_repository,
        syllabus_clo_repository=syllabus_clo_repository,
        assessment_scheme_repository=assessment_scheme_repository
    )
  

    # NEW SERVICES
    program_outcome_service = providers.Factory(
        ProgramOutcomeService,
        repository=program_outcome_repository,
        program_repository=program_repository
    )

    file_service = providers.Factory(
        FileService,
        repository=file_repository
    )

    clo_plo_mapping_service = providers.Factory(
        CloPloMappingService,
        repository=clo_plo_mapping_repository,
        syllabus_clo_repository=syllabus_clo_repository,
        program_outcome_repository=program_outcome_repository
    )

    subject_relationship_service = providers.Factory(
        SubjectRelationshipService,
        repository=subject_relationship_repository,
        subject_repository=subject_repository
    )

    syllabus_comment_service = providers.Factory(
        SyllabusCommentService,
        repository=syllabus_comment_repository,
        syllabus_repository=syllabus_repository,
        user_repository=user_repository
    )

    notification_service = providers.Factory(
        NotificationService,
        repository=notification_repository,
        user_repository=user_repository
    )

    system_setting_service = providers.Factory(
        SystemSettingService,
        repository=system_setting_repository
    )

    student_service = providers.Factory(
        StudentService, 
        sub_repo=student_subscription_repository,
        report_repo=student_report_repository
    )

    # AI Service (inject audit repository)
    from services.ai_service import AiService
    ai_service = providers.Factory(
        AiService,
        audit_repository=ai_auditlog_repository
    )

    role_service = providers.Factory(
        RoleService,
        repository=role_repository
    )

    user_service = providers.Factory(
        UserService,
        repository=user_repository
    )