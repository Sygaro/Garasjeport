# controllers/logger_controller.py

import os
from utils.log_utils import parse_log_file  # forutsetter at vi har det
from config.config_paths import LOG_DIR  # eller hardkod: "logs/"

class LoggerController:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir

    def get_recent_logs(self, filename="activity.log", limit=20):
        path = os.path.join(self.log_dir, filename)
        return parse_log_file(path, limit)
        
        if not os.path.exists(log_path):
            return []

        with open(log_path, "r") as f:
            for line in f.readlines()[-limit:]:
                entries.append({"time": line[:19], "message": line[20:].strip()})

        return entries
