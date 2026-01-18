from marshmallow import fields
from .base_schema import BaseSchema

class SyllabusCloSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(allow_none=True)
    code = fields.Str(required=True)
    description = fields.Str(required=True)
    plo_mappings = fields.List(fields.Nested('CloPloMappingSchema'), dump_only=True)
    created_at = fields.DateTime(dump_only=True)