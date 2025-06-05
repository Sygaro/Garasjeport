# pigpiod_monitor.py

import os
import subprocess
import time
import json
from datetime import datetime
from utils.logging.unified_logger import get_logger
from utils import config_paths
from monitor.monitor_registry import monitor_registry

logger = get_logger("pigpiod_monitor", category="system", source="SYSTEM")

STATUS_FILE = config_paths.STATUS_PIGPIO_STATUS_PATH


def is_pigpiod_running():
    try:
        output = subprocess.check_output(["pgrep", "pigpiod"])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False


def restart_pigpiod():
    try:
        subprocess.call(["sudo", "systemctl", "restart", "pigpiod"])
        logger.info("pigpiod ble restartet")
    except Exception as e:
        logger.error(f"Feil ved restart av pigpiod: {e}")


def load_status():
    if not os.path.exists(STATUS_FILE):
        return 0, None
    try:
        with open(STATUS_FILE, "r") as f:
            data = json.load(f)
            return data.get("restarts", 0), data.get("last_restart")
    except Exception as e:
        logger.warning(f"Kunne ikke laste pigpiod status: {e}")
        return 0, None


def write_status(running, restarts, last_restart):
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump({
                "running": running,
                "restarts": restarts,
                "last_restart": last_restart,
                "last_checked": datetime.now().isoformat()
            }, f)
        logger.debug("Status skrevet til fil: running=%s, restarts=%s", running, restarts)
    except Exception as e:
        logger.error(f"Kunne ikke skrive pigpiod status: {e}")


def start_pigpiod_monitor():
    logger.info("Starter pigpiod monitor")
    running = is_pigpiod_running()
    restarts, last_restart = load_status()

    if not running:
        restarts += 1
        last_restart = datetime.now().isoformat()
        restart_pigpiod()
        logger.warning("pigpiod ikke kjørende – restartes")

    write_status(running, restarts, last_restart)

    # Legg inn status i monitor_registry
    monitor_registry["pigpiod"] = {
        "running": running,
        "last_checked": datetime.now().isoformat(),
        "restarts": restarts,
        "last_restart": last_restart
    }

    logger.info("pigpiod monitor fullført")
