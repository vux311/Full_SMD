from marshmallow import Schema, fields

class ProgramSchema(Schema):
    id = fields.Int(dump_only=True)
    department_id = fields.Int(required=True)
    name = fields.Str(required=True)
    total_credits = fields.Int(load_default=0)