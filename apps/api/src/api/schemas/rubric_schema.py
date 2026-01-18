from marshmallow import fields
from .base_schema import BaseSchema

class RubricSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    component_id = fields.Int(allow_none=True)
    criteria = fields.Str(required=True)
    max_score = fields.Float(required=True)
    description_level_pass = fields.Str(load_default=None)
    description_level_fail = fields.Str(load_default=None)