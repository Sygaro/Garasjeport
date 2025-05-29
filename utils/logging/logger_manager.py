import os
import logging
from logging.handlers import RotatingFileHandler
from utils.config_loader import load_logging_config
from config import config_paths

# Last inn logging-konfigurasjon
default_config = {
    "log_directory": "logs",
    "max_file_size_mb": 10,
    "rotation_days": 14,
    "retention_days": 90,
    "timestamp_format": "%Y-%m-%d %H:%M:%S",
    "log_settings": {}
}

logging_config = load_logging_config()
CATEGORY_TO_PATH = {
    "status": config_paths.LOG_STATUS_PATH,
    "error": config_paths.LOG_ERROR_PATH,
    "activity": config_paths.LOG_ACTIVITY_PATH,
    "timing": config_paths.LOG_TIMING_PATH,
    "env": config_paths.LOG_SENSOR_ENV_PATH,
    "bootstrap": config_paths.LOG_BOOTSTRAP_PATH,
    "garage_controller": config_paths.LOG_GARAGE_CONTROLLER_PATH,
    "system_monitor": config_paths.LOG_GARAGE_CONTROLLER_PATH,

}

class LoggerManager:
    _loggers = {}

    @staticmethod
    def get_logger(name, category="default"):
        logger_id = f"{name}_{category}"
        if logger_id in LoggerManager._loggers:
            return LoggerManager._loggers[logger_id]

        log_settings = logging_config.get("log_settings", {}).get(category, {})
        log_level = getattr(logging, log_settings.get("level", "INFO"))
        log_format = log_settings.get("format", "plain")
        timestamp_format = logging_config.get("timestamp_format", "%Y-%m-%d %H:%M:%S")
        output_targets = log_settings.get("output", ["file"])  # "file", "console"

        logger = logging.getLogger(logger_id)
        logger.setLevel(log_level)
        logger.propagate = False

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt=timestamp_format
        ) if log_format == "plain" else logging.Formatter(
            fmt="{\"time\": \"%(asctime)s\", \"level\": \"%(levelname)s\", \"logger\": \"%(name)s\", \"message\": \"%(message)s\"}",
            datefmt=timestamp_format
        )

        log_file_path = CATEGORY_TO_PATH.get(category)
        max_bytes = logging_config.get("max_file_size_mb", 10) * 1024 * 1024

        if "file" in output_targets and log_file_path:
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            file_handler = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=5)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        if "console" in output_targets:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        LoggerManager._loggers[logger_id] = logger
        return logger

# For enkel tilgang
get_logger = LoggerManager.get_logger
