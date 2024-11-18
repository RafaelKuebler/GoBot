import logging
import sys


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s")

    # log_filename = datetime.now().isoformat()
    # file_handler = logging.FileHandler(f"logs/{log_filename}.log", "w")
    # file_handler.formatter = formatter
    # root_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.formatter = formatter
    root_logger.addHandler(stream_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
