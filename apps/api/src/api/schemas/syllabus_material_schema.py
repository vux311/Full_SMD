from marshmallow import fields
from .base_schema import BaseSchema

class SyllabusMaterialSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(allow_none=True)
    type = fields.Str(required=True)
    title = fields.Str(required=True)
    author = fields.Str(load_default=None)
    publisher = fields.Str(load_default=None)
    isbn = fields.Str(load_default=None)
    url = fields.Str(load_default=None)