from marshmallow import Schema, fields

class FacultySchema(Schema):
    id = fields.Int(dump_only=True)
    code = fields.Str(required=True)
    name = fields.Str(required=True)
    # Optional fields example: use load_default for Marshmallow
    description = fields.Str(load_default=None)
