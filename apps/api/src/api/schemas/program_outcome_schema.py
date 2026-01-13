from marshmallow import Schema, fields

class ProgramOutcomeSchema(Schema):
    id = fields.Int(dump_only=True)
    program_id = fields.Int(required=True)
    code = fields.Str(required=True)
    description = fields.Str(required=True)