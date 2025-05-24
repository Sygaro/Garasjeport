# controllers/logger_controller.py

import os
from utils.log_utils import parse_log_file
from config.config_paths import LOG_DIR  # bruker nå sentral sti
from utils.garage_logger import GarageLogger


class LoggerController:
    def __init__(self, log_dir=LOG_DIR):
        # Setter loggmappen via config_paths
        self.log_dir = log_dir

    def get_recent_logs(self, filename="activity.log", limit=20):
        # Leser siste X linjer fra loggfil
        path = os.path.join(self.log_dir, filename)
        return parse_log_file(path, limit)

# ✅ Instans opprettes etter klassen er definert
logger_controller = LoggerController()