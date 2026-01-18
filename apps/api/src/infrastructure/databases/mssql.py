from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from config import Config
from infrastructure.databases.base import Base

# Database configuration
DATABASE_URI = Config.DATABASE_URI

# Configure engine with proper connection pooling
engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_size=30,              # Connection pool size
    max_overflow=60,           # Additional connections beyond pool_size (Total 90)
    pool_pre_ping=True,        # Verify connection before use
    pool_recycle=3600,         # Recycle connection after 1 hour
    echo=Config.DEBUG,         # Log SQL queries in debug mode
    connect_args={
        'timeout': 30
    }
)

# Use sessionmaker to create a factory for Session objects
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False     # Don't expire objects after commit
)

# Create a scoped session for thread-safe usage across the application
# This is preferred for Flask applications as it provides one session per request/thread
db_session = scoped_session(SessionLocal)

# Alias for backward compatibility (mapped to the scoped session)
session = db_session

def init_mssql(app):
    """Initialize database with proper error handling."""
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Ensure that the database session is removed after each request."""
        db_session.remove()

    try:
        Base.metadata.create_all(bind=engine)
        app.logger.info("✓ Database tables created successfully")
    except Exception as e:
        app.logger.error(f"✗ Failed to create database tables: {e}")
        raise
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
