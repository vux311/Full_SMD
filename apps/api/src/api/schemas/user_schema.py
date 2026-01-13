from marshmallow import fields
from .base_schema import BaseSchema

class UserSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    full_name = fields.Str(required=True)
    department_id = fields.Int(load_default=None)
    is_active = fields.Bool(load_default=True)
    password = fields.Str(load_only=True, required=True)
