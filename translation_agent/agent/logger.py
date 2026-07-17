"""
LOGGER — Ghi log hoat dong cua Agent ra console.
"""
import logging


def setup_logger():
    """Thiet lap logger cho Agent. Chi in ra console."""
    logger = logging.getLogger("weather_agent")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_fmt)

    logger.addHandler(console_handler)
    return logger
