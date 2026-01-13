# from marshmallow import Schema, fields

# class SubjectSchema(Schema):
#     id = fields.Int(dump_only=True)
#     department_id = fields.Int(required=True)
#     code = fields.Str(required=True)
#     name_vi = fields.Str(required=True)
#     name_en = fields.Str(required=True)
#     credits = fields.Int(required=True)
#     credit_theory = fields.Float(missing=0)
#     credit_practice = fields.Float(missing=0)
#     credit_self_study = fields.Float(missing=0)
from marshmallow import Schema, fields

class SubjectSchema(Schema):
    id = fields.Int(dump_only=True)
    department_id = fields.Int(required=True)
    code = fields.Str(required=True)
    name_vi = fields.Str(required=True)
    name_en = fields.Str(required=True)
    credits = fields.Int(required=True)
    # Sửa missing=0 thành load_default=0
    credit_theory = fields.Float(load_default=0)
    credit_practice = fields.Float(load_default=0)
    credit_self_study = fields.Float(load_default=0)