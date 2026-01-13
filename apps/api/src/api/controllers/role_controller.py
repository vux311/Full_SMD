from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.role_service import RoleService
from api.schemas.role_schema import RoleSchema

role_bp = Blueprint('role', __name__, url_prefix='/roles')

schema = RoleSchema()

@role_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def list_roles(role_service: RoleService = Provide[Container.role_service]):
    """Get all roles
    ---
    get:
      summary: Get all roles
      tags:
        - Roles
      responses:
        200:
          description: List of roles
    """
    roles = role_service.list_roles()
    return jsonify(schema.dump(roles, many=True)), 200

@role_bp.route('/', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def create_role(role_service: RoleService = Provide[Container.role_service]):
    """Create a new role
    ---
    post:
      summary: Create a new role
      tags:
        - Roles
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Role'
      responses:
        201:
          description: Role created
        400:
          description: Invalid input
    """
    data = request.get_json() or {}
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    role = role_service.create_role(data)
    return jsonify(schema.dump(role)), 201