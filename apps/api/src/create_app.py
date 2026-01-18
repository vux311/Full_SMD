from flask import Flask
from config import Config
from api.middleware import middleware
from api.routes import register_routes
from infrastructure.databases import init_db
from utils.caching import cache
from utils.socket_io import init_socketio
from utils.mail import init_mail
from utils.logging_config import setup_logging as setup_structured_logging
from celery_utils import celery_init_app

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Celery
    celery_init_app(app)

    # Setup structured logging
    setup_structured_logging(
        app_name=app.config.get('APP_NAME', 'smd-api'),
        log_level=app.config.get('LOG_LEVEL', 'INFO'),
        log_dir=app.config.get('LOG_DIR', 'logs')
    )
    
    # Setup Flask-Caching
    cache.init_app(app, config={
        'CACHE_TYPE': app.config.get('CACHE_TYPE', 'SimpleCache'),
        'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300),
        'CACHE_REDIS_URL': app.config.get('CACHE_REDIS_URL')
    })

    init_db(app)
    init_socketio(app)
    init_mail(app)
    middleware(app)
    register_routes(app)

    return app