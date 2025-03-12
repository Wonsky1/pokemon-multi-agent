import logging
import sys
from pathlib import Path

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LOGS_DIR = Path("logs")
APP_LOG_FILE = LOGS_DIR / "app.log"
API_LOG_FILE = LOGS_DIR / "api.log"
AGENT_LOG_FILE = LOGS_DIR / "agents.log"


def setup_logger(
    name: str,
    level: int = logging.INFO,
    file_path: Path = None,
    console: bool = True,
    propagate: bool = False,
) -> logging.Logger:
    """
    Configure and return a logger with the specified parameters.

    Args:
        name: Name of the logger
        level: Logging level
        file_path: Path to log file (None for no file logging)
        console: Whether to log to console
        propagate: Whether to propagate to parent loggers

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = propagate

    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    if file_path:
        file_path.parent.mkdir(exist_ok=True, parents=True)

        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    return logger


def configure_all_loggers(debug_mode: bool = False):
    """
    Configure all application loggers.

    Args:
        debug_mode: If True, sets all loggers to DEBUG level
    """
    log_level = logging.DEBUG if debug_mode else logging.INFO

    root_logger = setup_logger(
        name="",
        level=log_level,
        file_path=APP_LOG_FILE,
        console=True,
        propagate=False,
    )

    setup_logger(
        name="agents",
        level=log_level,
        file_path=AGENT_LOG_FILE,
        console=False,
        propagate=True,
    )

    setup_logger(
        name="api",
        level=log_level,
        file_path=API_LOG_FILE,
        console=False,
        propagate=True,
    )

    setup_logger(
        name="tools",
        level=log_level,
        file_path=None,
        console=False,
        propagate=True,
    )

    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_error_logger = logging.getLogger("uvicorn.error")

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    for uvicorn_logger in (uvicorn_access_logger, uvicorn_error_logger):
        uvicorn_logger.handlers.clear()
        uvicorn_logger.setLevel(log_level)

        file_handler = logging.FileHandler(API_LOG_FILE)
        file_handler.setFormatter(formatter)
        uvicorn_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        uvicorn_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name. Uses existing logger if already configured.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
