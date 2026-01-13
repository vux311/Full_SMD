from marshmallow import Schema, fields

class WorkflowLogSchema(Schema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(required=True)
    actor_id = fields.Int(required=True)
    action = fields.Str(required=True)
    from_status = fields.Str(load_default=None)
    to_status = fields.Str(load_default=None)
    comment = fields.Str(load_default=None)
    created_at = fields.DateTime(dump_only=True)
