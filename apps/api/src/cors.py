from flask_cors import CORS

def init_cors(app):
    # Allow multiple origins including localhost variants
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
            "allow_headers": ["Authorization", "Content-Type", "X-Requested-With", "Accept"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600,
            "send_wildcard": False,
            "always_send": True
        }
    }, supports_credentials=True)
    app.config.setdefault('CORS_HEADERS', 'Content-Type')
    return app