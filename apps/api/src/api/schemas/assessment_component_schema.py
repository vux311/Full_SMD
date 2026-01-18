from marshmallow import fields, Schema
from marshmallow.validate import Range
from .rubric_schema import RubricSchema
from .base_schema import BaseSchema

class AssessmentCloSchema(BaseSchema):
    syllabus_clo_id = fields.Int(dump_only=True)
    syllabus_clo_code = fields.Str(attribute="syllabus_clo.code", dump_only=True)

class AssessmentComponentSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    scheme_id = fields.Int(allow_none=True)
    name = fields.Str(required=True)
    weight = fields.Float(required=True, validate=Range(min=0, max=100))
    criteria = fields.Str(allow_none=True)
    # Flexible field to accept either a list of IDs or a string of CLO codes
    clo_ids = fields.Raw(allow_none=True)
    rubrics = fields.List(fields.Nested('RubricSchema'), load_default=[])
    clos = fields.List(fields.Nested('AssessmentCloSchema'), dump_only=True)
