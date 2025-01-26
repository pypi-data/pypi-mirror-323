import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

# Log record format
LOG_RECORD = (
    "%(asctime)s|%(levelname)s|%(processName)s/%(process)d|%(threadName)s/%(thread)d|"
    "  %(name)s.%(funcName)s:%(lineno)d|%(message)s"
)

NAME_APP = "orca"
FOLDER_PATH = "logs"


def create_logs_folder_if_not_exists():
    """Create a folder if it does not exist."""
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)


class MinLevelFilter(logging.Filter):
    """
    Logging filter class to filter out all records that have a level between min_level and max_level.
    """

    def __init__(self, min_level: int, max_level: int):
        super().__init__()
        create_logs_folder_if_not_exists()

        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return self.min_level <= record.levelno <= self.max_level


def setup_stream_handler(
    stream, level_range: tuple[int, int], formatter: logging.Formatter
) -> logging.StreamHandler:
    """
    Create and configure a stream handler with a filter for specific log levels.
    """
    handler = logging.StreamHandler(stream)
    handler.addFilter(MinLevelFilter(*level_range))
    handler.setFormatter(formatter)
    return handler


def setup_file_handler(log_file: str, formatter: logging.Formatter) -> logging.Handler:
    """
    Create and configure a time-based rotating file handler that creates a new log file every day.
    """
    # Rotate the log at midnight every day
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1)
    file_handler.suffix = "%Y-%m-%d"  # Appends date to the log file name
    file_handler.setLevel(logging.DEBUG)  # Log everything (DEBUG and above)
    file_handler.setFormatter(formatter)
    file_handler.extMatch = r"^\d{4}-\d{2}-\d{2}$"  # Matches the date pattern
    return file_handler


def config_logging(
    logger_name: str,
    level: Optional[int] = logging.DEBUG,
) -> logging.Logger:
    """
    Configures and returns a logger that writes logs to both stdout (INFO and below) and stderr (ERROR and above),
    as well as to a log file that rotates every day.
    """
    # Formatter for log records
    formatter = logging.Formatter(LOG_RECORD)

    # Stream handlers
    stdout_handler = setup_stream_handler(
        sys.stdout, (logging.DEBUG, logging.WARNING), formatter
    )
    stderr_handler = setup_stream_handler(
        sys.stderr, (logging.ERROR, logging.CRITICAL), formatter
    )

    log_file = f'{FOLDER_PATH}/{logger_name}_{NAME_APP}_{datetime.now().strftime("%Y-%m-%d")}.log'
    # File handler with daily rotation
    file_handler = setup_file_handler(log_file, formatter)

    # Get or create logger
    logger = logging.getLogger(logger_name)

    # Determine logging level from environment if not provided
    if level is None:
        level = os.environ.get("LOGLEVEL", "DEBUG").upper()
        level = getattr(
            logging, level, logging.DEBUG
        )  # Fallback to DEBUG if level is invalid

    logger.setLevel(level)

    # Ensure logger has no duplicate handlers
    if not any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers):
        logger.addHandler(stdout_handler)
        logger.addHandler(stderr_handler)
        logger.addHandler(file_handler)

    return logger
