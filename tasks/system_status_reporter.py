# tasks/system_status_reporter.py

from monitor.monitor_registry import get_registry_status
from utils.logging.unified_logger import get_logger
import threading, time


EXPECTED_MONITORS = {"env_sensor_monitor", "port_sensor_monitor", "pigpiod_monitor"}

logger = get_logger("system_status_reporter", category="system", source="SYSTEM")

def system_status_reporter():
    logger.info("Starter system status reporter...")
    while True:
        try:
            status = get_registry_status()
            logger.info(f"Systemstatus: {status}")
        except Exception as e:
            logger.error(f"Feil i system_status_reporter: {e}")
        time.sleep(60)  # Juster etter behov


def check_monitor_health():
    logger.info("Sjekker helsen til alle monitorer...")
    status = get_registry_status()
    missing = EXPECTED_MONITORS - status.keys()

    for name, data in status.items():
        logger.info(f"Monitor aktiv: {name} @ {data['timestamp']}")

    for name in missing:
        logger.warning(f"Monitor IKKE aktiv: {name}")

def start_system_status_reporter():
    logger.info("Starter system status reporter tråd...")
    thread = threading.Thread(target=system_status_reporter, daemon=True)
    thread.start()
    logger.info("System status reporter started")
