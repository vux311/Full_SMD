import json
from marshmallow import fields, post_dump
from marshmallow.validate import Length
from .base_schema import BaseSchema
from .syllabus_clo_schema import SyllabusCloSchema
from .syllabus_material_schema import SyllabusMaterialSchema
from .teaching_plan_schema import TeachingPlanSchema
from .assessment_scheme_schema import AssessmentSchemeSchema
from .subject_schema import SubjectSchema
from .user_schema import UserSchema
from .program_schema import ProgramSchema
from .academic_year_schema import AcademicYearSchema

class SyllabusListSchema(BaseSchema):
    """Schema for syllabus list view with denormalized data"""
    id = fields.Int(dump_only=True)
    subject_code = fields.Str(dump_only=True)
    subject_name_vi = fields.Str(dump_only=True)
    subject_name_en = fields.Str(dump_only=True)
    credits = fields.Int(dump_only=True)
    lecturer = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    version = fields.Str(dump_only=True)
    date_edited = fields.DateTime(dump_only=True, attribute='updated_at')
    due_date = fields.DateTime(dump_only=True, attribute='current_workflow.due_date')

class SyllabusSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    subject_id = fields.Int(required=True)
    program_id = fields.Int(required=True)
    academic_year_id = fields.Int(required=True)
    lecturer_id = fields.Int(required=True)
    head_department_id = fields.Int(allow_none=True)
    dean_id = fields.Int(allow_none=True)

    status = fields.Str(dump_only=True)
    version = fields.Str(load_default="1.0", validate=Length(max=10))

    # Basic info for frontend display (read-only)
    subject_code = fields.Nested('SubjectSchema', only=('code',), dump_only=True, attribute='subject')
    subject_name_vi = fields.Nested('SubjectSchema', only=('name_vi',), dump_only=True, attribute='subject')
    subject_name_en = fields.Nested('SubjectSchema', only=('name_en',), dump_only=True, attribute='subject')
    credits = fields.Nested('SubjectSchema', only=('credits',), dump_only=True, attribute='subject')
    lecturer = fields.Nested('UserSchema', only=('full_name',), dump_only=True, attribute='lecturer')
    program_name = fields.Nested('ProgramSchema', only=('name',), dump_only=True, attribute='program')
    academic_year_name = fields.Nested('AcademicYearSchema', only=('code',), dump_only=True, attribute='academic_year')

    # Workflow deadline info
    due_date = fields.DateTime(dump_only=True, attribute='current_workflow.due_date')
    assigned_to = fields.Nested('UserSchema', only=('full_name',), dump_only=True, attribute='current_workflow.assigned_to_user')

    @post_dump
    def flatten_subject_info(self, data, **kwargs):
        # Flatten nested subject/lecturer fields into top-level strings
        # Note: Hooks in BaseSchema (to_camel) may run BEFORE or AFTER this 
        # depending on Marshmallow version and configuration. We check both keys.
        
        # subjectCode / subject_code
        sc = data.get('subjectCode') or data.get('subject_code')
        if isinstance(sc, dict):
            val = sc.get('code')
            if 'subjectCode' in data: data['subjectCode'] = val
            if 'subject_code' in data: data['subject_code'] = val
            
        # subjectNameVi / subject_name_vi
        snv = data.get('subjectNameVi') or data.get('subject_name_vi')
        if isinstance(snv, dict):
            val = snv.get('name_vi') or snv.get('nameVi')
            if 'subjectNameVi' in data: data['subjectNameVi'] = val
            if 'subject_name_vi' in data: data['subject_name_vi'] = val
            
        # subjectNameEn / subject_name_en
        sne = data.get('subjectNameEn') or data.get('subject_name_en')
        if isinstance(sne, dict):
            val = sne.get('name_en') or sne.get('nameEn')
            if 'subjectNameEn' in data: data['subjectNameEn'] = val
            if 'subject_name_en' in data: data['subject_name_en'] = val
            
        # credits
        cre = data.get('credits')
        if isinstance(cre, dict):
            val = cre.get('credits')
            data['credits'] = val
            
        # lecturer
        lec = data.get('lecturer')
        if isinstance(lec, dict):
            val = lec.get('full_name') or lec.get('fullName')
            data['lecturer'] = val

        # program_name
        prog = data.get('programName') or data.get('program_name')
        if isinstance(prog, dict):
            val = prog.get('name')
            if 'programName' in data: data['programName'] = val
            if 'program_name' in data: data['program_name'] = val

        # academic_year_name
        ay = data.get('academicYearName') or data.get('academic_year_name')
        if isinstance(ay, dict):
            val = ay.get('code')
            if 'academicYearName' in data: data['academicYearName'] = val
            if 'academic_year_name' in data: data['academic_year_name'] = val

        # assigned_to
        ast = data.get('assignedTo') or data.get('assigned_to')
        if isinstance(ast, dict):
            val = ast.get('full_name') or ast.get('fullName')
            if 'assignedTo' in data: data['assignedTo'] = val
            if 'assigned_to' in data: data['assigned_to'] = val
            
        return data

    # FIX: time_allocation as Dict -> Use Raw to accept DB-stored JSON string
    time_allocation = fields.Raw(allow_none=True)  # Changed from Dict to Raw to handle DB String
    prerequisites = fields.Str(load_default=None)
    
    # Content fields
    description = fields.Str(allow_none=True)
    objectives = fields.Raw(allow_none=True)  # JSON array
    student_duties = fields.Str(allow_none=True)
    other_requirements = fields.Str(allow_none=True)
    
    # Additional metadata
    pre_courses = fields.Str(allow_none=True)
    co_courses = fields.Str(allow_none=True)
    course_type = fields.Str(allow_none=True)
    component_type = fields.Str(allow_none=True)
    date_prepared = fields.Str(allow_none=True)
    date_edited = fields.Str(allow_none=True)
    dean = fields.Str(allow_none=True)
    dean_id = fields.Int(allow_none=True)
    head_department = fields.Str(allow_none=True)
    head_department_id = fields.Int(allow_none=True)
    
    publish_date = fields.DateTime(load_default=None)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # FIX: Add nested fields for input (load_default=[])
    clos = fields.List(fields.Nested('SyllabusCloSchema'), load_default=[])
    materials = fields.List(fields.Nested('SyllabusMaterialSchema'), load_default=[])
    teaching_plans = fields.List(fields.Nested('TeachingPlanSchema'), load_default=[])
    assessment_schemes = fields.List(fields.Nested('AssessmentSchemeSchema'), load_default=[])

    @post_dump
    def parse_json(self, data, **kwargs):
        # Parse time_allocation JSON (checks both formats)
        ta = data.get('timeAllocation') or data.get('time_allocation')
        if isinstance(ta, str):
            try:
                val = json.loads(ta)
                if 'timeAllocation' in data: data['timeAllocation'] = val
                if 'time_allocation' in data: data['time_allocation'] = val
            except:
                pass
        
        # Parse objectives JSON array
        obj = data.get('objectives')
        if isinstance(obj, str):
            try:
                data['objectives'] = json.loads(obj)
            except:
                pass
        
        return data