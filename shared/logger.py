"""
Logging utilities
"""

import logging
import sys
import io
from pathlib import Path

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """Setup logger for a service"""

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler with UTF-8 encoding support
    # This fixes Windows console encoding issues with emojis
    try:
        # Try to use UTF-8 encoding for console output
        if hasattr(sys.stdout, 'buffer'):
            # Wrap stdout with UTF-8 encoding
            stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
        else:
            stream = sys.stdout
    except (AttributeError, io.UnsupportedOperation):
        # Fallback to default stdout
        stream = sys.stdout

    console_handler = logging.StreamHandler(stream)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (optional) - always use UTF-8
    if log_file:
        Path("logs").mkdir(exist_ok=True)
        file_handler = logging.FileHandler(f"logs/{log_file}", encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)

    return logger
