from marshmallow import Schema, fields

class SyllabusCommentSchema(Schema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    content = fields.Str(required=True)
    parent_id = fields.Int(load_default=None)
    is_resolved = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)