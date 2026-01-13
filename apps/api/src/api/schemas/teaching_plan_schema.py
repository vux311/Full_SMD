from marshmallow import Schema, fields

class TeachingPlanSchema(Schema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(required=True)
    week = fields.Int(required=True)
    topic = fields.Str(load_default=None)
    activity = fields.Str(load_default=None)
    assessment = fields.Str(load_default=None)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)