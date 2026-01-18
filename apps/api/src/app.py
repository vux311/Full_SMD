from flask import Flask, jsonify
from api.swagger import spec
from api.middleware import middleware
from infrastructure.databases import init_db
from flasgger import Swagger
from flask_swagger_ui import get_swaggerui_blueprint
from cors import init_cors

# Dependency injection
from dependency_container import Container
from api.controllers.subject_controller import subject_bp
from api.controllers.faculty_controller import faculty_bp
from api.controllers.department_controller import department_bp
from api.controllers.role_controller import role_bp
from api.controllers.user_controller import user_bp
from api.controllers.academic_year_controller import academic_year_bp
from api.controllers.program_controller import program_bp
from api.controllers.syllabus_controller import syllabus_bp
from api.controllers.syllabus_clo_controller import syllabus_clo_bp
from api.controllers.syllabus_material_controller import syllabus_material_bp
from api.controllers.teaching_plan_controller import teaching_plan_bp
from api.controllers.assessment_scheme_controller import assessment_scheme_bp
from api.controllers.assessment_component_controller import assessment_component_bp
from api.controllers.rubric_controller import rubric_bp
from api.controllers.assessment_clo_controller import assessment_clo_bp
from api.controllers.auth_controller import auth_bp
from api.controllers.ai_controller import ai_bp
from api.controllers.dashboard_controller import dashboard_bp
from api.controllers.program_outcome_controller import program_outcome_bp
from api.controllers.file_controller import file_bp
from api.controllers.clo_plo_mapping_controller import clo_plo_mapping_bp
from api.controllers.subject_relationship_controller import subject_rel_bp
from api.controllers.syllabus_comment_controller import syllabus_comment_bp
from api.controllers.notification_controller import notification_bp
from api.controllers.system_setting_controller import system_setting_bp
from api.controllers.student_controller import student_bp
from api.controllers.search_controller import search_bp
from api.controllers.public_controller import public_bp
from api.controllers.admin_controller import admin_bp
from utils.socket_io import socketio, init_socketio


def create_app():
    app = Flask(__name__)

    # Initialize CORS early so Swagger and other blueprints respect it
    try:
        init_cors(app)
    except Exception:
        pass

    Swagger(app)
    # Using async_mode='threading' or 'gevent' is often more stable on Windows for development 
    # if eventlet produces WinError 10038
    try:
        init_socketio(app)
    except Exception as e:
        print(f"[WARNING] SocketIO init failure: {e}")

    # Initialize DI container and wire controllers
    container = Container()
    # Wire the container explicitly for controllers
    try:
        container.wire(modules=[
            "api.controllers.subject_controller",
            "api.controllers.faculty_controller",
            "api.controllers.department_controller",
            "api.controllers.role_controller",
            "api.controllers.user_controller",
            "api.controllers.academic_year_controller",
            "api.controllers.program_controller",
            "api.controllers.syllabus_controller",
            "api.controllers.syllabus_clo_controller",
            "api.controllers.syllabus_material_controller",
            "api.controllers.teaching_plan_controller",
            "api.controllers.assessment_scheme_controller",
            "api.controllers.assessment_component_controller",
            "api.controllers.rubric_controller",
            "api.controllers.assessment_clo_controller",
            "api.controllers.auth_controller",
            "api.controllers.ai_controller",
            "api.controllers.dashboard_controller",
            "api.controllers.program_outcome_controller",
            "api.controllers.file_controller",
            "api.controllers.clo_plo_mapping_controller",
            "api.controllers.subject_relationship_controller",
            "api.controllers.syllabus_comment_controller",
            "api.controllers.notification_controller",
            "api.controllers.system_setting_controller",
            "api.controllers.student_controller",
            "api.controllers.search_controller",
            "api.controllers.public_controller",
            "api.controllers.admin_controller",
        ])
        print("[OK] Dependency injection wiring successful")
    except Exception as e:
        error_msg = f"Failed to wire dependency container: {e}"
        print(f"[ERROR] {error_msg}")
        import os
        # In production, fail fast; in development, allow partial wiring
        if os.getenv('ENVIRONMENT', 'development') == 'production':
            raise RuntimeError(error_msg)
        else:
            print("[WARNING] Continuing with incomplete DI wiring in development mode")

    # Register blueprints
    app.register_blueprint(subject_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(academic_year_bp)
    app.register_blueprint(program_bp)
    app.register_blueprint(syllabus_bp)
    app.register_blueprint(syllabus_clo_bp)
    app.register_blueprint(syllabus_material_bp)
    app.register_blueprint(teaching_plan_bp)
    app.register_blueprint(assessment_scheme_bp)
    app.register_blueprint(assessment_component_bp)
    app.register_blueprint(rubric_bp)
    app.register_blueprint(assessment_clo_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(program_outcome_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(clo_plo_mapping_bp)
    app.register_blueprint(subject_rel_bp)
    app.register_blueprint(syllabus_comment_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(system_setting_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

     # Thêm Swagger UI blueprint
    SWAGGER_URL = '/docs'
    API_URL = '/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Syllabus Management API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Database initialization with proper error handling
    try:
        init_db(app)
        print("[OK] Database initialized successfully")
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        import os
        if os.getenv('ENVIRONMENT', 'development') == 'production':
            raise

    # Register middleware
    middleware(app)
    print("[OK] Middleware registered")

    # Initialize CORS
    try:
        init_cors(app)
    except Exception:
        pass

    # Register routes (add all non-static endpoints to Swagger where possible)
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            if rule.endpoint == 'static':
                continue
            view_func = app.view_functions.get(rule.endpoint)
            if not view_func:
                continue
            try:
                spec.path(view=view_func)
                print(f"Adding path: {rule.rule} -> {view_func}")
            except Exception:
                # some endpoints may not be compatible with flasgger, skip them
                pass

    @app.route("/swagger.json")
    def swagger_json():
        return jsonify(spec.to_dict())

    return app
# Run the application

if __name__ == '__main__':
    print("Starting app initialization...")
    app = create_app()
    print("App created, starting socketio...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 
