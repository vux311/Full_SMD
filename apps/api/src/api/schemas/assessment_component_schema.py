from marshmallow import Schema, fields
from marshmallow.validate import Range

class AssessmentComponentSchema(Schema):
    id = fields.Int(dump_only=True)
    scheme_id = fields.Int(required=True)
    name = fields.Str(required=True)
    weight = fields.Float(required=True, validate=Range(min=0, max=100))
    rubrics = fields.List(fields.Nested('RubricSchema'), dump_only=True)