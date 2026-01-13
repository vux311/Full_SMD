from marshmallow import Schema, fields

class StudentSubscriptionSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(required=True)
    subject_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)

class StudentReportSchema(Schema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(required=True)
    student_id = fields.Int(required=True)
    content = fields.Str(required=True)
    status = fields.Str(dump_only=True)
    admin_note = fields.Str(load_default=None)