from marshmallow import fields
from api.schemas.base_schema import BaseSchema

class AcademicYearSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    code = fields.Str(required=True)
    start_date = fields.Date(required=False, allow_none=True)  # Optional
    end_date = fields.Date(required=False, allow_none=True)    # Optional
    is_active = fields.Bool(required=False)                    # Optional

