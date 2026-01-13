from marshmallow import Schema, fields

class DepartmentSchema(Schema):
    id = fields.Int(dump_only=True)
    faculty_id = fields.Int(required=True)
    code = fields.Str(required=True)
    name = fields.Str(required=True)
