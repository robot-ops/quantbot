from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import config
from loguru import logger

Base = declarative_base()

engine_args = {}
# Specific config for SQLite to allow multiple threads
if config.database_url.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

try:
    engine = create_engine(config.database_url, **engine_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info(f"Database engine initialized for {config.database_url.split('://')[0]}://...")
except Exception as e:
    logger.error(f"Error initializing database engine: {e}")
    # Fallback to in-memory SQLite if database URL is misconfigured
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.warning("Fallback database in-memory SQLite engine initialized.")

def init_db():
    """Create all tables defined on Base."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

def get_db():
    """Dependency for getting a database session context."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
