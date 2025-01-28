"""Configure logging for the Contensis Management API."""

import logging


def configure_logging(level=logging.DEBUG):
    """Configure logging for the Contensis Management API."""
    # Set up the root logger with handlers, formatters, etc.
    logger = logging.getLogger()
    logger.setLevel(level)

    # Set up a console handler with a specific format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Avoid adding multiple handlers if this function is called multiple times
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger
