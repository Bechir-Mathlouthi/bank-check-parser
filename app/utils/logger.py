import logging
import logging.handlers
import os
from datetime import datetime

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """Configure logger with file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    if log_file:
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            f'logs/{log_file}',
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 