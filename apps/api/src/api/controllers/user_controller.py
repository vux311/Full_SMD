from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.user_service import UserService
from services.system_auditlog_service import SystemAuditLogService
from api.schemas.user_schema import UserSchema
from api.middleware import token_required, role_required

user_bp = Blueprint('user', __name__, url_prefix='/users')

schema = UserSchema()

@user_bp.route('/', methods=['GET'], strict_slashes=False)
@token_required
@inject
def list_users(user_service: UserService = Provide[Container.user_service]):
    """Get all users
    ---
    get:
      summary: Get all users
      tags:
        - Users
      responses:
        200:
          description: List of users
    """
    users = user_service.list_users()
    return jsonify(schema.dump(users, many=True)), 200

@user_bp.route('/<int:id>', methods=['GET'], strict_slashes=False)
@inject
def get_user(id: int, user_service: UserService = Provide[Container.user_service]):
    """Get user by id
    ---
    get:
      summary: Get user by ID
      tags:
        - Users
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: User object
        404:
          description: Not found
    """
    user = user_service.get_user(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(schema.dump(user)), 200


@user_bp.route('/<int:id>', methods=['DELETE'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def delete_user(id: int, 
                user_service: UserService = Provide[Container.user_service],
                audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """
    Delete a user
    ---
    delete:
      summary: Delete user by ID
      tags:
        - Users
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: User deleted successfully
        404:
          description: User not found
    """
    # Get user info before deleting for logging
    user = user_service.get_user_by_id(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Delete the user
    success = user_service.delete_user(id)
    if not success:
        return jsonify({'message': 'Failed to delete user'}), 500
    
    # Log the action
    try:
        # Get current user from token if available
        current_user_id = getattr(request, 'user_id', None)
        audit_service.create_log(
            user_id=current_user_id,
            action_type='DELETE_USER',
            resource_target=f'User #{id} ({user.username})',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f'Deleted user: {user.full_name} (Username: {user.username}, Email: {user.email})'
        )
    except Exception as e:
        print(f"Failed to log audit: {e}")
    
    return jsonify({'message': 'User deleted successfully'}), 200


@user_bp.route('/me', methods=['GET'], strict_slashes=False)
@inject
@token_required
def get_me(user_service: UserService = Provide[Container.user_service]):
    """
    Get current user from token
    """
    from flask import g
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        return jsonify({'message': 'User not found in token'}), 401
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get role name from user
    role_name = None
    try:
        if user.roles and len(user.roles) > 0 and getattr(user.roles[0], 'role', None):
            role_name = user.roles[0].role.name
    except Exception:
        role_name = None
    
    # Build response with role
    user_data = schema.dump(user)
    user_data['role'] = role_name
    
    return jsonify(user_data), 200

@user_bp.route('/', methods=['POST'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def create_user(user_service: UserService = Provide[Container.user_service],
                audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Create a new user
    ---
    post:
      summary: Create a new user
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      responses:
        201:
          description: User created
        400:
          description: Invalid input
    """
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    user = user_service.create_user(data)
    
    # Log the action
    try:
        current_user_id = getattr(request, 'user_id', None)
        audit_service.create_log(
            user_id=current_user_id,
            action_type='CREATE_USER',
            resource_target=f'User #{user.id} ({user.username})',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f'Created new user: {user.full_name} (Username: {user.username}, Email: {user.email})'
        )
    except Exception as e:
        print(f"Failed to log audit: {e}")
    
    return jsonify(schema.dump(user)), 201

@user_bp.route('/<int:id>', methods=['PUT'], strict_slashes=False)
@token_required
@role_required(['Admin'])
@inject
def update_user(id: int, 
                user_service: UserService = Provide[Container.user_service],
                audit_service: SystemAuditLogService = Provide[Container.system_auditlog_service]):
    """Update an existing user
    ---
    put:
      summary: Update user
      tags:
        - Users
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      responses:
        200:
          description: User updated
        400:
          description: Invalid input
        404:
          description: User not found
    """
    data = request.get_json() or {}
    errors = schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400
    user = user_service.update_user(id, data)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Log the action
    try:
        current_user_id = getattr(request, 'user_id', None)
        # Build details of what was updated
        updated_fields = ', '.join([f"{k}={v}" for k, v in data.items() if k not in ['password', 'password_hash']])
        audit_service.create_log(
            user_id=current_user_id,
            action_type='UPDATE_USER',
            resource_target=f'User #{user.id} ({user.username})',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f'Updated user: {user.full_name} - Changes: {updated_fields}'
        )
    except Exception as e:
        print(f"Failed to log audit: {e}")
    
    return jsonify(schema.dump(user)), 200


@user_bp.route('/<int:user_id>/roles', methods=['POST'], strict_slashes=False)
@inject
def assign_roles_to_user(user_id: int, user_service: UserService = Provide[Container.user_service]):
    """
    Assign roles to a user
    ---
    post:
      summary: Assign roles to user
      tags:
        - Users
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                role_ids:
                  type: array
                  items:
                    type: integer
      responses:
        200:
          description: Roles assigned successfully
        404:
          description: User not found
    """
    from infrastructure.models.user_role_model import UserRole
    from infrastructure.databases.mssql import session as db_session
    
    data = request.get_json() or {}
    role_ids = data.get('role_ids', [])
    
    if not role_ids:
        return jsonify({'message': 'No role_ids provided'}), 400
    
    # Check if user exists
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    try:
        # Remove existing roles for this user
        deleted_count = db_session.query(UserRole).filter_by(user_id=user_id).delete(synchronize_session='fetch')
        print(f"Deleted {deleted_count} existing roles for user {user_id}")
        
        # Add new roles
        for role_id in role_ids:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            db_session.add(user_role)
            print(f"Added role {role_id} to user {user_id}")
        
        # Flush to get any errors before commit
        db_session.flush()
        
        # Commit the transaction
        db_session.commit()
        
        print(f"Successfully committed roles for user {user_id}")
        return jsonify({
            'message': 'Roles assigned successfully', 
            'user_id': user_id,
            'role_ids': role_ids
        }), 200
    except Exception as e:
        db_session.rollback()
        print(f"Error assigning roles: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error assigning roles: {str(e)}'}), 500