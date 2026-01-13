from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from config import Config
from infrastructure.databases.base import Base

# Database configuration
DATABASE_URI = Config.DATABASE_URI

# Configure engine with proper connection pooling
engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_size=20,              # Connection pool size
    max_overflow=40,           # Additional connections beyond pool_size
    pool_pre_ping=True,        # Verify connection before use
    pool_recycle=3600,         # Recycle connection after 1 hour
    echo=Config.DEBUG,         # Log SQL queries in debug mode
    connect_args={
        'timeout': 30
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False     # Don't expire objects after commit
)

# Create a default session for backward compatibility (not recommended for use)
# NOTE: DI Container should use SessionLocal() factory instead
session = SessionLocal()

def init_mssql(app):
    """Initialize database with proper error handling."""
    try:
        Base.metadata.create_all(bind=engine)
        app.logger.info("✓ Database tables created successfully")
    except Exception as e:
        app.logger.error(f"✗ Failed to create database tables: {e}")
        raise