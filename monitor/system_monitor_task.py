import threading
import time
from config import config_paths as paths
from utils.logging.unified_logger import get_logger
from utils.system_monitor import get_system_status, check_thresholds_and_log
from utils.config_loader import load_config

logger = get_logger("system_monitor", category="system", source="health")

def start_system_monitor_task():
    def monitor_loop():
        while True:
            try:
                config = load_config(paths.CONFIG_HEALTH_PATH)
                interval = config.get("alerts", {}).get("interval_minutes") or 15
                status = get_system_status()
                warnings = check_thresholds_and_log(status)

                if config.get("alerts", {}).get("log_warning", True):
                    logger.info(f"Statussjekk OK: {status}")

            except Exception as e:
                logger.error(f"Feil i monitor-task: {e}")

            time.sleep(interval * 60)

    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    logger.info("System monitor task startet")
    return thread  