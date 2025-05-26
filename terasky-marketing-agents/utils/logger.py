import logging
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime

def setup_logger(name: str = "terasky_marketing") -> logging.Logger:
    """Set up and configure the application logger."""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(f"logs/{name}_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create formatters
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set formatters
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(json_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def get_agent_logger(agent_name: str) -> logging.Logger:
    """Get a logger instance for a specific agent."""
    return setup_logger(f"terasky_marketing.{agent_name}")

def log_agent_activity(logger: logging.Logger, agent_name: str, activity: str, level: str = "info"):
    """Log agent activity with consistent formatting."""
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(f"[{agent_name}] {activity}")

def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """Log error with consistent formatting."""
    error_message = str(error)
    if context:
        error_message = f"{context} - {error_message}"
    logger.error(error_message, exc_info=True) 