from marshmallow import fields
from .base_schema import BaseSchema

class RoleSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(load_default=None)