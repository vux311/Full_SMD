from flask_socketio import SocketIO
from utils.logging_config import get_logger

logger = get_logger(__name__)

socketio = SocketIO(cors_allowed_origins="*")

def init_socketio(app):
    """Initialize SocketIO with the Flask app"""
    logger.info("Initializing SocketIO...")
    socketio.init_app(app)

def notify_user(user_id, event, data):
    """Send a notification to a specific user via SocketIO"""
    room = f"user_{user_id}"
    logger.info(f"Emitting {event} to room {room}")
    socketio.emit(event, data, room=room)

def broadcast_notification(event, data):
    """Broadcast a notification to all connected users"""
    logger.info(f"Broadcasting {event}")
    socketio.emit(event, data)
