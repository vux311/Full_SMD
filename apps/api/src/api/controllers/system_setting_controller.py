from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.system_setting_service import SystemSettingService
from api.schemas.system_setting_schema import SystemSettingSchema
from api.middleware import token_required, role_required

system_setting_bp = Blueprint('system_setting', __name__, url_prefix='/settings')
schema = SystemSettingSchema()

@system_setting_bp.route('/', methods=['GET'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def list_settings(service: SystemSettingService = Provide[Container.system_setting_service]):
    """
    List all system settings (Admin only)
    """
    items = service.get_all_settings()
    return jsonify(schema.dump(items, many=True)), 200

@system_setting_bp.route('/<string:key>', methods=['PUT'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def update_setting(key: str, service: SystemSettingService = Provide[Container.system_setting_service]):
    """
    Update a system setting (Admin only)
    """
    data = request.get_json() or {}
    value = data.get('value')
    if value is None:
        return jsonify({"error": "Value is required"}), 400
        
    item = service.update_setting(key, str(value), data.get('description'))
    return jsonify(schema.dump(item)), 200