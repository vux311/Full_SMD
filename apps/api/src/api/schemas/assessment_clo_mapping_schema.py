from marshmallow import Schema, fields

class AssessmentCloMappingSchema(Schema):
    assessment_component_id = fields.Int(required=True)
    syllabus_clo_id = fields.Int(required=True)