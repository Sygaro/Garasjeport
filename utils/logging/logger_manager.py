# Fil: utils/logging/logger_manager.py

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from utils.logging.log_config_loader import load_logging_config
from config.log_categories import LOG_CATEGORIES

_initialized_loggers = {}
_formatter_cache = {}

def _get_formatter(fmt_type: str, timestamp_fmt: str) -> logging.Formatter:
    key = f"{fmt_type}_{timestamp_fmt}"
    if key not in _formatter_cache:
        if fmt_type == "plain":
            fmt = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt=timestamp_fmt
            )
        else:
            # Allow custom format strings
            fmt = logging.Formatter(fmt_type, datefmt=timestamp_fmt)
        _formatter_cache[key] = fmt
    return _formatter_cache[key]

def get_logger(name: str, category: str = "default") -> logging.Logger:
    if category not in LOG_CATEGORIES:
        fallback_logger = logging.getLogger(f"fallback_{name}")
        fallback_logger.setLevel(logging.ERROR)
        if not fallback_logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter("%(asctime)s [FALLBACK] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            fallback_logger.addHandler(handler)
        fallback_logger.error(f"Ugyldig loggkategori: '{category}' brukt i modul '{name}'")
        return fallback_logger

    logger_key = f"{name}_{category}"
    if logger_key in _initialized_loggers:
        return _initialized_loggers[logger_key]

    config = load_logging_config()
    log_settings = config.get("log_settings", {}).get(category, {})
    log_directory = config.get("log_directory", "logs")
    timestamp_format = config.get("timestamp_format", "%Y-%m-%d %H:%M:%S")
    max_file_size_mb = config.get("max_file_size_mb", 10)
    rotation_days = config.get("rotation_days", 14)

    level_str = log_settings.get("level", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    enabled = log_settings.get("enabled", True)
    output = log_settings.get("output", ["file"])
    fmt_type = log_settings.get("format", "plain")

    logger = logging.getLogger(logger_key)
    logger.setLevel(level)
    logger.propagate = False

    formatter = _get_formatter(fmt_type, timestamp_format)

    if enabled:
        if "file" in output and category in LOG_CATEGORIES:
            os.makedirs(log_directory, exist_ok=True)
            file_path = LOG_CATEGORIES[category]
            file_handler = RotatingFileHandler(
                file_path, maxBytes=max_file_size_mb * 1024 * 1024, backupCount=rotation_days
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        if "console" in output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    _initialized_loggers[logger_key] = logger
    logger.debug(f"Logger '{logger_key}' initialized with level {level_str}, output: {output}")
    return logger
