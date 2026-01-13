from marshmallow import Schema, fields
from marshmallow.validate import OneOf

class SubjectRelationshipSchema(Schema):
    id = fields.Int(dump_only=True)
    subject_id = fields.Int(required=True)
    related_subject_id = fields.Int(required=True)
    type = fields.Str(required=True, validate=OneOf(['PREREQUISITE', 'COREQUISITE', 'PARALLEL']))