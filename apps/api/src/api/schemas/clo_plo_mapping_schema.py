from marshmallow import Schema, fields
from marshmallow.validate import OneOf

class CloPloMappingSchema(Schema):
    id = fields.Int(dump_only=True)
    syllabus_clo_id = fields.Int(required=True)
    program_plo_id = fields.Int(required=True)
    level = fields.Str(required=True, validate=OneOf(['I', 'R', 'M', 'A']))