from marshmallow import Schema, fields
from marshmallow.validate import Range

class AssessmentSchemeSchema(Schema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(required=True)
    name = fields.Str(required=True)
    weight = fields.Float(required=True, validate=Range(min=0, max=100))
    components = fields.List(fields.Nested('AssessmentComponentSchema'), dump_only=True)