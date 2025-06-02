# Fil: utils/logging/unified_logger.py

from utils.logging.logger_manager import get_logger as core_get_logger
from config.log_levels import LOG_LEVELS
import logging



class UnifiedLogger:
    def __init__(self, name, category, source=None):
        self.logger = core_get_logger(name, category, source)

        self.category = category
        self.source = source
        print(f"[DEBUG] Init logger: name={name}, category={category}, source={source}")


    def _wrap(self, level, msg):
        extra = {"category": self.category}
        if self.source:
            extra["source"] = self.source
        getattr(self.logger, level)(msg, extra=extra)

    def debug(self, msg):
        self._wrap("debug", msg)

    def info(self, msg):
        self._wrap("info", msg)

    def warning(self, msg):
        self._wrap("warning", msg)

    def error(self, msg):
        self._wrap("error", msg)

    def critical(self, msg):
        self._wrap("critical", msg)

    def change(self, msg, *args, **kwargs):
        level = LOG_LEVELS.get("CHANGE", logging.INFO)
        self.logger.log(level, msg, *args, **kwargs)

    def timing(self, msg, *args, **kwargs):
        level = LOG_LEVELS.get("TIMING", logging.INFO)
        self.logger.log(level, msg, *args, **kwargs)



# Nytt anbefalt grensesnitt:
def get_logger(name, category="system", source=None):
    return UnifiedLogger(name, category, source)
