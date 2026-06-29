from __future__ import annotations

import logging
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
APP_LOG_PATH = LOG_DIR / "app.log"
ERROR_LOG_PATH = LOG_DIR / "error.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(level_name: str = "INFO") -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, level_name.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    app_handler = logging.FileHandler(APP_LOG_PATH, encoding="utf-8")
    app_handler.setLevel(level)
    app_handler.setFormatter(formatter)

    error_handler = logging.FileHandler(ERROR_LOG_PATH, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)

    logger = logging.getLogger("desktop_companion_ai")
    logger.debug("Logging initialized")
    return logger
