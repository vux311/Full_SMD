import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # apps/api/src
try:
    import services.syllabus_service as ss
    import services.ai_service as ai
    import api.schemas.syllabus_schema as sch
    import services.program_outcome_service as plo_svc
    import api.controllers.program_outcome_controller as plo_ctrl
    import services.file_service as file_svc
    import api.controllers.file_controller as file_ctrl
    import services.clo_plo_mapping_service as mapping_svc
    import api.controllers.clo_plo_mapping_controller as mapping_ctrl
    import services.subject_relationship_service as rel_svc
    import api.controllers.subject_relationship_controller as rel_ctrl
    import services.syllabus_comment_service as comment_svc
    import api.controllers.syllabus_comment_controller as comment_ctrl
    import services.notification_service as notif_svc
    import api.controllers.notification_controller as notif_ctrl
    import infrastructure.repositories.ai_auditlog_repository as audit_repo
    import services.system_setting_service as ss_svc
    import api.controllers.system_setting_controller as ss_ctrl
    import services.student_service as student_svc
    import api.controllers.student_controller as student_ctrl
    print('IMPORT_OK')
except Exception as e:
    print('IMPORT_FAIL', repr(e))
    raise