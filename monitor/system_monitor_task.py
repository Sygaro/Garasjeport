import threading
import time

from utils.system_monitor import get_system_status, check_thresholds_and_log
from utils.config_loader import load_config
from config import config_paths as paths
from utils.logging.logger_manager import get_logger

logger = get_logger("system_monitor")
status_logger = get_logger("system_monitor", category="system_monitor")

def start_system_monitor_task():
    def monitor_loop():
        while True:
            try:
                config = load_config(paths.CONFIG_HEALTH_PATH)
                interval = config.get("alerts", {}).get("interval_minutes", 15)
                status = get_system_status()
                warnings = check_thresholds_and_log(status)

                if config.get("alerts", {}).get("log_warning", True):
                    status_logger.status("system_monitor", f"Statussjekk OK: {status}")

            except Exception as e:
                logger.log_error("system_monitor", f"Feil i monitor-task: {e}")

            time.sleep(interval * 60)

    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
