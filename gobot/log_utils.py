import logging
import sys

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
LOG_LEVEL = logging.INFO


def setup_logging():
    root_logger = logging.getLogger()

    # Clear existing handlers (e.g., AWS Lambda adds one by default)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT)
    stream_handler.setFormatter(formatter)

    root_logger.addHandler(stream_handler)
    root_logger.setLevel(LOG_LEVEL)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
