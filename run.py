import logging
from app import create_app
from app.config.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting Flask server...")
        app = create_app()
        logger.info(f"Flask server starting on http://localhost:5000")
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=settings.DEBUG
        )
    except Exception as e:
        logger.error(f"Failed to start Flask server: {str(e)}")
        raise

if __name__ == "__main__":
    main() 