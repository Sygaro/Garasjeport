# unified_logger.py
from utils.logging.logger_manager import get_logger as core_get_logger

def get_logger(name, category="system"):
    return core_get_logger(name, category)
