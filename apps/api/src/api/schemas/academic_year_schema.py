from marshmallow import Schema, fields

class AcademicYearSchema(Schema):
    id = fields.Int(dump_only=True)
    code = fields.Str(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
