from marshmallow import Schema, fields

class ProgramSchema(Schema):
    id = fields.Int(dump_only=True)
    department_id = fields.Int(required=True)
    name = fields.Str(required=True)
    total_credits = fields.Int(load_default=0)
    
    # Nested department info
    department = fields.Nested('DepartmentSchema', only=('id', 'name', 'code'), dump_only=True)