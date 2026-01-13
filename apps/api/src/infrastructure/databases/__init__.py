from infrastructure.databases.mssql import init_mssql
from infrastructure.models import (
    academic_year_model,
    ai_auditlog_model,
    assessment_clo_model,
    assessment_component_model,
    assessment_scheme_model,
    clo_plo_mapping_model,
    department_model,
    faculty_model,
    file_model,
    notification_model,
    notification_template_model,
    program_model,
    program_outcome_model,
    role_model,
    rubric_model,
    student_report_model,
    student_subscription_model,
    subject_model,
    subject_relationship_model,
    syllabus_clo_model,
    syllabus_comment_model,
    syllabus_current_workflow,
    syllabus_material_model,
    syllabus_model,
    system_auditlog_model,
    system_setting_model,
    teaching_plan_model,
    user_model,
    user_role_model,
    workflow_log_model,
    workflow_state_model,
    workflow_transition_model
)

def init_db(app):
    init_mssql(app)

# Migration Entities -> tables
from infrastructure.databases.mssql import Base