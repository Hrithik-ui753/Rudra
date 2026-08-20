import logging
import sys
from typing import Optional


def setup_logger(name: str = "rudra", level: str = "INFO") -> logging.Logger:
    """Configures and returns a structured logger for the RUDRA backend."""
    logger_obj = logging.getLogger(name)
    
    if not logger_obj.handlers:
        logger_obj.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger_obj.addHandler(handler)
        
        # Prevent propagation to root logger to avoid duplicate log entries
        logger_obj.propagate = False

    return logger_obj


# Global logger instance
logger = setup_logger()
