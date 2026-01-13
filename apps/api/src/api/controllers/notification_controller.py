from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.notification_service import NotificationService
from api.schemas.notification_schema import NotificationSchema
from api.middleware import token_required

notification_bp = Blueprint('notification', __name__, url_prefix='/notifications')
schema = NotificationSchema()

@notification_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
@token_required
def get_my_notifications(service: NotificationService = Provide[Container.notification_service]):
    """
    Get current user's notifications
    ---
    tags:
      - Notifications
    parameters:
      - name: unread
        in: query
        type: boolean
        description: Filter by unread only
    responses:
      200:
        description: List of notifications
    """
    from flask import g
    user_id = getattr(g, 'user_id', None)
    if not user_id:
         return jsonify({'message': 'User context missing'}), 401
    unread = request.args.get('unread', 'false').lower() == 'true'
    items = service.get_user_notifications(user_id, unread_only=unread)
    return jsonify(schema.dump(items, many=True)), 200

@notification_bp.route('/<int:id>/read', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
@token_required
def mark_read(id: int, service: NotificationService = Provide[Container.notification_service]):
    """
    Mark a notification as read
    ---
    tags:
      - Notifications
    parameters:
      - name: id
        in: path
        required: true
        schema: {type: integer}
    responses:
      200:
        description: Marked as read
    """
    ok = service.mark_read(id)
    if not ok:
        return jsonify({'message': 'Notification not found'}), 404
    return jsonify({'message': 'Marked as read'}), 200