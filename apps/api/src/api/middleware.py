# Middleware functions for processing requests and responses

from flask import  request, jsonify

def log_request_info(app):
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

def handle_options_request():
    return jsonify({'message': 'CORS preflight response'}), 200

from flask import current_app
from werkzeug.exceptions import HTTPException
import traceback

def error_handling_middleware(error):
    # Handle HTTP exceptions (e.g., BadRequest) with their status codes
    if isinstance(error, HTTPException):
        response = jsonify({'error': error.description})
        response.status_code = error.code or 400
        return response

    # Log unexpected exceptions with traceback
    try:
        current_app.logger.exception(error)
    except Exception:
        pass

    tb = None
    try:
        tb = traceback.format_exc()
    except Exception:
        tb = None

    payload = {'error': str(error)}
    if getattr(current_app, 'debug', False) and tb:
        payload['traceback'] = tb

    response = jsonify(payload)
    response.status_code = 500
    return response

def add_custom_headers(response):
    response.headers['X-Custom-Header'] = 'Value'
    return response

from functools import wraps


def middleware(app):
    @app.before_request
    def before_request():
        log_request_info(app)

    @app.after_request
    def after_request(response):
        return add_custom_headers(response)

    @app.errorhandler(Exception)
    def handle_exception(error):
        return error_handling_middleware(error)

    @app.route('/options', methods=['OPTIONS'])
    def options_route():
        return handle_options_request()


# Token decorator verifying JWT
import jwt
from config import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, make_response, g
        # Allow preflight CORS requests through without authentication
        if request.method == 'OPTIONS':
            return make_response('', 200)
        auth = request.headers.get('Authorization', '')
        if not auth or not auth.startswith('Bearer '):
            return jsonify({'message': 'Authorization token is missing'}), 401
        token = auth.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            # Attach user info to Flask g context
            g.user_id = payload.get('user_id')
            g.username = payload.get('username')
            g.role = payload.get('role')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)

    return decorated


# Role-based access control decorator
def role_required(allowed_roles):
    """
    Decorator to restrict access to specific roles.
    Usage: @role_required(['Admin', 'Head of Dept'])
    
    Args:
        allowed_roles: List of role names that are allowed to access the endpoint
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask import g, jsonify, request, make_response
            
            # Allow preflight CORS requests through
            if request.method == 'OPTIONS':
                return make_response('', 200)
            
            # Get role from Flask g context (set by @token_required)
            user_role = getattr(g, 'role', None)
            
            if not user_role:
                return jsonify({
                    'message': 'Role information not found. Please login again.'
                }), 403
            
            # Check if user's role is in allowed roles
            if user_role not in allowed_roles:
                return jsonify({
                    'message': f'Access denied. Required roles: {", ".join(allowed_roles)}',
                    'your_role': user_role
                }), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator