from marshmallow import fields
from .base_schema import BaseSchema

class TeachingPlanSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(allow_none=True)
    week = fields.Int(required=True)
    topic = fields.Str(load_default=None)
    clos = fields.Str(load_default=None)
    activity = fields.Str(load_default=None)
    assessment = fields.Str(load_default=None)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)