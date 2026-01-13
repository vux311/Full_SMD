from marshmallow import Schema, fields

class NotificationSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    title = fields.Str(required=True)
    message = fields.Str(load_default=None)
    link = fields.Str(load_default=None)
    is_read = fields.Bool(dump_only=True)
    type = fields.Str(load_default='SYSTEM')
    created_at = fields.DateTime(dump_only=True)