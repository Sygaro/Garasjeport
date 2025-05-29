# logger_manager.py
import logging
import os
from logging.handlers import RotatingFileHandler
from config import config_paths
from utils.logging.log_config import load_logging_config

CATEGORY_TO_PATH = {
    "status": config_paths.LOG_STATUS_PATH,
    "error": config_paths.LOG_ERROR_PATH,
    "activity": config_paths.LOG_ACTIVITY_PATH,
    "timing": config_paths.LOG_TIMING_PATH,
    "env": config_paths.LOG_SENSOR_ENV_PATH,
    "bootstrap": config_paths.LOG_BOOTSTRAP_PATH,
    "controller": config_paths.LOG_GARAGE_CONTROLLER_PATH,
    "default": config_paths.LOG_STATUS_PATH,
    "garage_controller": config_paths.LOG_GARAGE_CONTROLLER_PATH,
    "system_monitor": config_paths.LOG_GARAGE_CONTROLLER_PATH,

}

_logging_config = load_logging_config()
_formatter_cache = {}
_logger_cache = {}

def _get_formatter(fmt_type):
    if fmt_type not in _formatter_cache:
        if fmt_type == "plain":
            fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", 
                                    datefmt=_logging_config.get("timestamp_format", "%Y-%m-%d %H:%M:%S"))
        else:
            fmt = logging.Formatter(fmt_type)  # fallback
        _formatter_cache[fmt_type] = fmt
    return _formatter_cache[fmt_type]

def get_logger(name, category="default"):
    cache_key = f"{name}_{category}"
    if cache_key in _logger_cache:
        return _logger_cache[cache_key]

    settings = _logging_config.get("log_settings", {}).get(category, {})
    if not settings.get("enabled", True):
        logger = logging.getLogger(name)
        logger.addHandler(logging.NullHandler())
        _logger_cache[cache_key] = logger
        return logger

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.get("level", "INFO")))
    logger.handlers = []

    formatter = _get_formatter(settings.get("format", "plain"))

    if "file" in settings.get("output", []):
        path = CATEGORY_TO_PATH.get(category, config_paths.LOG_STATUS_PATH)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        file_handler = RotatingFileHandler(
            path,
            maxBytes=_logging_config.get("max_file_size_mb", 10) * 1024 * 1024,
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if "console" in settings.get("output", []):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    _logger_cache[cache_key] = logger
    return logger
