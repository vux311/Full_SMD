from marshmallow import fields
from marshmallow.validate import Range
from .assessment_component_schema import AssessmentComponentSchema
from .base_schema import BaseSchema

class AssessmentSchemeSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(allow_none=True)
    name = fields.Str(required=True)
    weight = fields.Float(load_default=100.0, validate=Range(min=0, max=100))
    components = fields.List(fields.Nested('AssessmentComponentSchema'), load_default=[])