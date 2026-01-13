from marshmallow import fields
from .base_schema import BaseSchema

class SyllabusDetailSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    subject_id = fields.Int(required=True)
    program_id = fields.Int(required=True)
    academic_year_id = fields.Int(required=True)
    lecturer_id = fields.Int(required=True)

    status = fields.Str(dump_only=True)
    version = fields.Str(dump_default="1.0")
    time_allocation = fields.Str(load_default=None)
    prerequisites = fields.Str(load_default=None)
    publish_date = fields.DateTime(load_default=None)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    clos = fields.List(fields.Nested('SyllabusCloSchema'), dump_only=True)
    materials = fields.List(fields.Nested('SyllabusMaterialSchema'), dump_only=True)
    teaching_plans = fields.List(fields.Nested('TeachingPlanSchema'), dump_only=True)
    assessment_schemes = fields.List(fields.Nested('AssessmentSchemeSchema'), dump_only=True)
