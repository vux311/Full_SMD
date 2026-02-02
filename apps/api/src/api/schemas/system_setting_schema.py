from marshmallow import Schema, fields

class SystemSettingSchema(Schema):
    key = fields.Str(required=True)
    value = fields.Str(required=True)
    data_type = fields.Str(dump_only=True)
    description = fields.Str(load_default=None)