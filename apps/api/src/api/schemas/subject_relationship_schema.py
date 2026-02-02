from marshmallow import Schema, fields, post_dump
from marshmallow.validate import OneOf

class SubjectRelationshipSchema(Schema):
    id = fields.Int(dump_only=True)
    subject_id = fields.Int(required=True)
    related_subject_id = fields.Int(required=True)
    type = fields.Str(required=True, validate=OneOf(['PREREQUISITE', 'COREQUISITE', 'CO_REQUISITE', 'PARALLEL', 'EQUIVALENT']))

    # Denormalized fields for UI
    related_subject_code = fields.Str(dump_only=True, attribute='related_subject.code')
    related_subject_name = fields.Str(dump_only=True, attribute='related_subject.name_vi')

    @post_dump
    def to_camel(self, data, **kwargs):
        # simple camelCase converter for this schema
        return {
            "id": data.get("id"),
            "subjectId": data.get("subject_id"),
            "relatedSubjectId": data.get("related_subject_id"),
            "type": data.get("type"),
            # Flattened fields for some UI components (e.g. VisualSubjectTree)
            "relatedSubjectCode": data.get("related_subject_code"),
            "relatedSubjectName": data.get("related_subject_name"),
            # Nested object for SubjectsPage admin modal
            "relatedSubject": {
                "id": data.get("related_subject_id"),
                "code": data.get("related_subject_code"),
                "nameVi": data.get("related_subject_name"),
                "name_vi": data.get("related_subject_name")
            }
        }