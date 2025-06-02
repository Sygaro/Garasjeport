# Fil: utils/logging/logger_manager.py

import logging
import logging.handlers
import os
from pathlib import Path
from config.log_categories import LOG_CATEGORIES
from utils.logging import log_config_loader

_formatter_cache = {}
_logger_cache = {}

# Last inn loggkonfigurasjon
log_config = log_config_loader.load_logging_config()
log_levels = log_config_loader.get_log_levels()

class SafeFormatter(logging.Formatter):
    def format(self, record):
        try:
            if not hasattr(record, "category"):
                record.category = "unknown_category"
            if not hasattr(record, "source"):
                record.source = "-"
            return super().format(record)
        except Exception:
            return f"[FORMATTER ERROR] {record.__dict__}"

def _get_formatter(fmt_type: str, timestamp_fmt: str) -> logging.Formatter:
    """
    Returnerer en formatter basert på valgt format-type ('plain' eller 'json').
    Resultatet caches for ytelse.
    """
    key = f"{fmt_type}_{timestamp_fmt}"
    if key not in _formatter_cache:
        if fmt_type == "plain":
            fmt = SafeFormatter(
                "%(asctime)s [%(levelname)s] %(name)s_%(category)s_%(source)s [-]: %(message)s",
                datefmt=timestamp_fmt
            )
        elif fmt_type == "json":
            fmt = SafeFormatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "category": "%(category)s", "source": "%(source)s", "message": "%(message)s"}',
                datefmt=timestamp_fmt
            )
        else:
            raise ValueError(f"Ugyldig formatter-type: '{fmt_type}'. Må være 'plain' eller 'json'.")
        _formatter_cache[key] = fmt
    return _formatter_cache[key]

def get_logger(name: str, category: str = "system", source: str = None) -> logging.Logger:
    if category not in LOG_CATEGORIES:
        fallback = logging.getLogger("FALLBACK")
        if not fallback.handlers:
            fallback.setLevel(logging.ERROR)
            fallback.addHandler(logging.StreamHandler())
        fallback.error("Ugyldig loggkategori: '%s' brukt i modul '%s'", category, name)
        return fallback

    unique_logger_name = f"{name}_{category}_{source or '-'}"
    if unique_logger_name in _logger_cache:
        return _logger_cache[unique_logger_name]

    logger = logging.getLogger(unique_logger_name)
    logger.setLevel(log_levels.get(category, logging.INFO))

    config = log_config.get("log_settings", {}).get(category, {})
    log_dir = Path(config.get("log_directory", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    fmt_type = config.get("format", "plain")
    timestamp_fmt = config.get("timestamp_format", log_config.get("timestamp_format", "%Y-%m-%d %H:%M:%S"))
    formatter = _get_formatter(fmt_type, timestamp_fmt)

    # File handler
    if config.get("file_enabled", True):
        file_path = log_dir / config.get("filename", f"{category}.log")
        max_bytes = config.get("max_bytes", log_config.get("max_file_size_mb", 10) * 1024 * 1024)
        backup_count = config.get("max_backups_files", log_config.get("max_backups_files", 5))
        file_handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(config.get("file_level", "DEBUG"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.debug("Filbasert logging aktivert: %s, maks %sMB, %d backup-filer",
                     file_path, max_bytes // (1024 * 1024), backup_count)

    # Console handler (hvis aktivert)
    if config.get("console_enabled", True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(config.get("console_level", "INFO"))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.debug("Console logging aktivert")

    logger.debug("Logger initialisert for modul: %s, kategori: %s, source: %s", name, category, source)
    _logger_cache[unique_logger_name] = logger
    return logger
