from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./checks.db"
)

try:
    logger.info(f"Initializing database connection: {SQLALCHEMY_DATABASE_URL}")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = scoped_session(SessionLocal)

    Base = declarative_base()
    Base.query = db_session.query_property()

    def init_db():
        """Initialize the database"""
        try:
            logger.info("Creating database tables...")
            import app.models.check  # Import models
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            raise

    def get_db():
        """Get database session"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise 