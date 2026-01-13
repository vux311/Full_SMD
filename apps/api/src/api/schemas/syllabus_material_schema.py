from marshmallow import Schema, fields

class SyllabusMaterialSchema(Schema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(required=True)
    type = fields.Str(required=True)
    title = fields.Str(required=True)
    author = fields.Str(load_default=None)
    publisher = fields.Str(load_default=None)
    isbn = fields.Str(load_default=None)
    url = fields.Str(load_default=None)