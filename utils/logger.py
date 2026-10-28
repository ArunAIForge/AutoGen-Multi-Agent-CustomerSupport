import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "customer_support", log_level: str = "INFO") -> logging.Logger:
    """Configures a centralized rotating file and console logger."""
    os.makedirs("logs", exist_ok=True)
    log_file = os.path.join("logs", "agent_activity.log")
    
    logger = logging.getLogger(name)
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(numeric_level)
        logger.addHandler(console_handler)
        
    return logger

app_logger = setup_logger()