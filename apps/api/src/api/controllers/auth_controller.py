from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.user_service import UserService
from services.system_auditlog_service import SystemAuditLogService
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'], strict_slashes=False)
@inject
def login(user_service: UserService = Provide[Container.user_service],
          audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """
    Login and obtain a token
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
              password:
                type: string
            required:
              - username
              - password
    responses:
      200:
        description: Login successful, returns token and user information
      400:
        description: Missing username or password
      401:
        description: Invalid credentials
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'username and password are required'}), 400
    user = user_service.get_by_username(username)
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    if not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Get role name if available
    role_name = None
    try:
        if user.roles and len(user.roles) > 0 and getattr(user.roles[0], 'role', None):
            role_name = user.roles[0].role.name
    except Exception:
        role_name = None

    # Generate real JWT token
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': role_name,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    
    # Log successful login
    try:
        audit_service.create_log(
            user_id=user.id,
            action_type='LOGIN',
            resource_target=f'User #{user.id} ({user.username})',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f'User logged in: {user.full_name} ({user.username})'
        )
    except Exception as e:
        print(f"Failed to log audit: {e}")
    
    return jsonify({
        'access_token': token,
        'token': token,  # Keep for backward compatibility
        'user_id': user.id, 
        'role': role_name
    }), 200