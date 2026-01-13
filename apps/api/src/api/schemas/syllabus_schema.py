import json
from marshmallow import fields, post_dump
from marshmallow.validate import Length
from .base_schema import BaseSchema

class SyllabusSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    subject_id = fields.Int(required=True)
    program_id = fields.Int(required=True)
    academic_year_id = fields.Int(required=True)
    lecturer_id = fields.Int(required=True)

    status = fields.Str(dump_only=True)
    version = fields.Str(load_default="1.0", validate=Length(max=10))
    
    # FIX: time_allocation as Dict -> Use Raw to accept DB-stored JSON string
    time_allocation = fields.Raw(allow_none=True)  # Changed from Dict to Raw to handle DB String
    prerequisites = fields.Str(load_default=None)
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
        if 'timeAllocation' in data and isinstance(data['timeAllocation'], str):
            try:
                data['timeAllocation'] = json.loads(data['timeAllocation'])
            except:
                pass
        return data