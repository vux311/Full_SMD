from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.user_service import UserService
from api.schemas.user_schema import UserSchema
from api.middleware import token_required

user_bp = Blueprint('user', __name__, url_prefix='/users')

schema = UserSchema()

@user_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
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

@user_bp.route('/<int:id>', methods=['GET', 'OPTIONS'], strict_slashes=False)
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


@user_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'], strict_slashes=False)
@inject
def delete_user(id: int, user_service: UserService = Provide[Container.user_service]):
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
    success = user_service.delete_user(id)
    if not success:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'message': 'User deleted successfully'}), 200


@user_bp.route('/me', methods=['GET', 'OPTIONS'], strict_slashes=False)
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

@user_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_user(user_service: UserService = Provide[Container.user_service]):
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
    return jsonify(schema.dump(user)), 201

@user_bp.route('/<int:id>', methods=['PUT', 'OPTIONS'], strict_slashes=False)
@inject
def update_user(id: int, user_service: UserService = Provide[Container.user_service]):
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
    return jsonify(schema.dump(user)), 200