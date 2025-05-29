# unified_logger.py
from utils.logging.logger_manager import get_logger as core_get_logger

def get_logger(name, category="default"):
    return core_get_logger(name, category)
