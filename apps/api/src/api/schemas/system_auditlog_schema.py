from marshmallow import fields, post_dump
from api.schemas.base_schema import BaseSchema

class SystemAuditLogSchema(BaseSchema):
    """Schema for system audit log serialization"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    action_type = fields.Str()
    resource_target = fields.Str(allow_none=True)
    ip_address = fields.Str(allow_none=True)
    user_agent = fields.Str(allow_none=True)
    details = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    
    # Nested user information
    user = fields.Nested('UserSchema', only=('id', 'username', 'full_name'), dump_only=True)
    
    @post_dump
    def transform_for_frontend(self, data, **kwargs):
        """Transform to match frontend expected format"""
        # Map createdAt (from BaseSchema camelCase) to timestamp
        if 'createdAt' in data:
            data['timestamp'] = data['createdAt']
        
        # Map actionType (from BaseSchema camelCase) to action
        if 'actionType' in data:
            data['action'] = data['actionType']
        
        # Extract username from nested user object
        if 'user' in data and data['user']:
            data['username'] = data['user'].get('username', 'Unknown')
        else:
            data['username'] = 'System'
        
        return data
