from marshmallow import fields
from .base_schema import BaseSchema
from .role_schema import RoleSchema

class UserRoleSchema(BaseSchema):
    """Nested schema for user_role relationship"""
    role_id = fields.Int()
    role = fields.Nested(RoleSchema, only=['id', 'name', 'description'])

class UserSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    full_name = fields.Str(required=True)
    department_id = fields.Int(load_default=None)
    avatar_file_id = fields.Int(load_default=None, allow_none=True)
    is_active = fields.Bool(load_default=True)
    password = fields.Str(load_only=True, required=True)
    roles = fields.Nested(UserRoleSchema, many=True, dump_only=True)
