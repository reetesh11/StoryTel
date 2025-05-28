import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Set up a logger with both file and console handlers
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # # Create formatters
    # file_formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s -  %(levelname)s - %(message)s'
    )

    # Create and configure file handler
    # if log_file is None:
    #     log_file = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    # file_handler = logging.FileHandler(log_dir / log_file)
    # file_handler.setLevel(logging.DEBUG)
    # file_handler.setFormatter(file_formatter)

    # Create and configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    # logger.addHandler(file_handler) 
    logger.addHandler(console_handler)

    return logger 