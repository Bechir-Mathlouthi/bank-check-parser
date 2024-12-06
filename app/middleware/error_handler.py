from functools import wraps
from flask import jsonify
import logging
from typing import Type, Callable
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API Exception"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def handle_errors(func: Callable) -> Callable:
    """Error handling decorator for API routes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            logger.error(f"API Error: {str(e)}")
            return jsonify({'error': e.message}), e.status_code
        except SQLAlchemyError as e:
            logger.error(f"Database Error: {str(e)}")
            return jsonify({'error': 'Database error occurred'}), 500
        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}")
            return jsonify({'error': 'An unexpected error occurred'}), 500
    return wrapper 