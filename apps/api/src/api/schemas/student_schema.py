from marshmallow import fields
from .base_schema import BaseSchema
from .user_schema import UserSchema

class StudentSubscriptionSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(required=True)
    subject_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)

class StudentReportSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    syllabus_id = fields.Int(required=True)
    student_id = fields.Int(required=True)
    content = fields.Str(required=True)
    status = fields.Str(dump_only=True)
    admin_note = fields.Str(load_default=None)
    created_at = fields.DateTime(dump_only=True)
    
    # Relationships
    user = fields.Nested(UserSchema, attribute='student', dump_only=True, only=['full_name', 'username'])
    syllabus = fields.Nested('SyllabusSchema', dump_only=True, only=['subject_code', 'subject_name_vi', 'version'])
