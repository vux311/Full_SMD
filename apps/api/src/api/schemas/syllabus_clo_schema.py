from marshmallow import Schema, fields

class SyllabusCloSchema(Schema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(required=True)
    code = fields.Str(required=True)
    description = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)