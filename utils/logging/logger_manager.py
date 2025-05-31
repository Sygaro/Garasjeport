# Fil: utils/logging/logger_manager.py

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from utils.logging.log_config_loader import load_logging_config
from config.log_categories import LOG_CATEGORIES

_initialized_loggers = {}
_formatter_cache = {}

class SafeFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "category"):
            record.category = "-"
        return super().format(record)

def _get_formatter(fmt_type: str, timestamp_fmt: str) -> logging.Formatter:
    key = f"{fmt_type}_{timestamp_fmt}"
    if key not in _formatter_cache:
        if fmt_type == "plain":
            fmt = SafeFormatter(
                "%(asctime)s [%(levelname)s] %(name)s_%(category)s [-]: %(message)s",
                datefmt=timestamp_fmt
            )
        else:
            fmt = SafeFormatter(fmt_type, datefmt=timestamp_fmt)
        _formatter_cache[key] = fmt
    return _formatter_cache[key]

def get_logger(name: str, category: str = "default") -> logging.Logger:
    config = load_logging_config()
    log_settings = config.get("log_settings", {})
    timestamp_fmt = config.get("timestamp_format", "%Y-%m-%d %H:%M:%S")
    log_dir = config.get("log_directory", "logs")
    max_file_size_mb = config.get("max_file_size_mb", 10)
    rotation_days = config.get("rotation_days", 7)

    if category not in LOG_CATEGORIES and category != "console_debug":
        fallback_logger = logging.getLogger(f"fallback_{name}")
        fallback_logger.setLevel(logging.ERROR)
        if not fallback_logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter("%(asctime)s [FALLBACK] %(levelname)s: %(message)s"))
            fallback_logger.addHandler(handler)
        fallback_logger.error(f"Ugyldig loggkategori: '{category}' brukt i modul '{name}'")
        return fallback_logger

    logger_key = f"{name}_{category}"
    if logger_key in _initialized_loggers:
        return _initialized_loggers[logger_key]

    logger = logging.getLogger(logger_key)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    category_config = log_settings.get(category, {})
    fmt_type = category_config.get("format", "plain")
    formatter = _get_formatter(fmt_type, timestamp_fmt)

    if category_config.get("file_enabled", False) and category in LOG_CATEGORIES:
        os.makedirs(log_dir, exist_ok=True)
        file_path = LOG_CATEGORIES[category]
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=rotation_days
        )
        file_handler.setLevel(category_config.get("file_level", "DEBUG").upper())
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if category_config.get("console_enabled", False):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(category_config.get("console_level", "INFO").upper())
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    adapter = logging.LoggerAdapter(logger, {"category": category})
    _initialized_loggers[logger_key] = adapter
    return adapter
