import json
import logging
from config import config_paths

def setup_logger():
    config_path = config_paths.CONFIG_BOOTSTRAP_PATH
    if not config_path.exists():
        raise FileNotFoundError(f"Fant ikke bootstrap logg-konfigurasjon: {config_path}")

    with config_path.open() as f:
        config = json.load(f)

    logger = logging.getLogger("bootstrap")
    logger.setLevel(getattr(logging, config.get("level", "INFO").upper(), logging.INFO))

    # Fjern eventuelle tidligere handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    formatter_type = config.get("format", "plain")
    if formatter_type == "json":
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    if config.get("console", True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if config.get("file", True):
        file_handler = logging.FileHandler(config_paths.LOG_BOOTSTRAP_PATH)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def shutdown_bootstrap_logger():
    logger = logging.getLogger("bootstrap")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    logger.disabled = True
