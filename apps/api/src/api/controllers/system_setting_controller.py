from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.system_setting_service import SystemSettingService
from api.schemas.system_setting_schema import SystemSettingSchema

system_setting_bp = Blueprint('system_setting', __name__, url_prefix='/system-settings')
schema = SystemSettingSchema()

@system_setting_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def list_settings(service: SystemSettingService = Provide[Container.system_setting_service]):
    """
    List all system settings
    ---
    tags:
      - System Settings
    responses:
      200:
        description: List of settings
    """
    items = service.get_all_settings()
    return jsonify(schema.dump(items, many=True)), 200

@system_setting_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def update_setting(service: SystemSettingService = Provide[Container.system_setting_service]):
    """
    Update or create a system setting
    ---
    tags:
      - System Settings
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/SystemSetting'
    responses:
      200:
        description: Setting updated
      400:
        description: Validation error
    """
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    item = service.update_setting(data['key'], data['value'], data.get('description'))
    return jsonify(schema.dump(item)), 200