import logging
import os
from logging.handlers import RotatingFileHandler
from config import config_paths
from utils.config_loader import load_config

_loggers = {}

class NullLogger:
    def __getattr__(self, name):
        def no_op(*args, **kwargs):
            pass
        return no_op

def get_logger(name: str, category: str = "status") -> logging.Logger:
    """
    Returnerer en logger basert på navngitt kategori:
    - 'status', 'error', 'activity', 'timing', 'bootstrap', 'sensor'
    Leser nivå og aktiv-status fra config_logging.json,
    men bruker path fra config_paths.py
    """
    if name in _loggers:
        return _loggers[name]

    config = load_config(config_paths.CONFIG_LOGGING_PATH)
    log_format = config.get("format", "text").lower()
    max_bytes = config.get("max_file_size_kb", 1024) * 1024
    backup_count = config.get("backup_count", 5)

    enabled = config.get("enabled_logs", {}).get(category, True)
    if not enabled:
        null_logger = NullLogger()
        _loggers[name] = null_logger
        return null_logger

    log_level_str = config.get("log_levels", {}).get(category, "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    path_map = {
        "status": config_paths.STATUS_LOG,
        "error": config_paths.ERROR_LOG,
        "activity": config_paths.ACTIVITY_LOG,
        "timing": config_paths.TIMING_LOG,
        "bootstrap": config_paths.BOOTSTRAP_LOG if hasattr(config_paths, 'BOOTSTRAP_LOG') else config_paths.STATUS_LOG,
        "sensor": config_paths.SENSOR_LOG_PATH
    }

    log_path = path_map.get(category, config_paths.STATUS_LOG)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False

    if not logger.handlers:
        if log_format == "json":
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "context": "%(name)s", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

        handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _loggers[name] = logger
    return logger
