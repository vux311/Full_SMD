from marshmallow import Schema, fields

class FileSchema(Schema):
    id = fields.Int(dump_only=True)
    uploader_id = fields.Int(dump_only=True)
    file_name = fields.Str(dump_only=True)
    file_path = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)