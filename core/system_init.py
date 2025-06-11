# core/system_init.py

"""
core/system_init.py (utdrag for monitor-integrasjon)
Integrerer MonitorManager i system-initiering og shutdown.
Bruker prosjektets standard for import av paths.
"""

import json, os #, sys, signal
from utils.logging.unified_logger import get_logger
from core.system import get_controller
from config import config_paths as paths
from monitor.system_monitor_task import start_system_monitor_task
from monitor.env_sensor_monitor_task import run_sensor_monitor_loop
from monitor.monitor_manager import MonitorManager
#from monitor.port_status_monitor import PortStatusMonitor
#from monitor.env_sensor_monitor import EnvSensorMonitor
#from utils.config_helpers import load_config
#from monitor.monitor_manager import MonitorManager


import threading
import atexit


logger = get_logger("system_init", category="system")

def load_json_config(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"Leste konfigurasjon: {path}")
        return data
    except Exception as e:
        logger.error(f"Kunne ikke lese konfigurasjon fra {path}: {e}", exc_info=True)
        raise


def init():
    logger.info("=== Starter systeminitiering ===")

    # Last konfigurasjoner fra fil via paths
    try:
        config_gpio = load_json_config(paths.CONFIG_GPIO_PATH)
        config_system = load_json_config(paths.CONFIG_PORT_STATUS_PATH)
        relay_pins = config_gpio.get("relay_pins") or []  # eller bruk riktig nøkkel
        relay_config = config_gpio.get("relay_config") or {}  # eller bruk riktig nøkkel
        testing_mode = config_system.get("testing_mode", False)
    except Exception as e:
        logger.error(f"Feil ved lasting av konfigurasjon: {e}", exc_info=True)
        raise

    try:
        controller = get_controller(
            config_gpio=config_gpio,
            config_system=config_system,
            relay_pins=relay_pins,
            relay_config=relay_config,
            testing_mode=testing_mode,
        )
        logger.info("GarageController initialisert OK.")
    except Exception as e:
        logger.error(f"Feil under initiering av GarageController: {e}", exc_info=True)
        raise

    try:
        logger.info("Starter system monitor task ...")
        start_system_monitor_task()
        logger.info("System monitor task startet OK.")
    except Exception as e:
        logger.error(f"Feil under oppstart av system_monitor_task: {e}", exc_info=True)
        raise

    try:
        logger.info("Starter sensor monitor (bakgrunnstråd)...")
        threading.Thread(target=run_sensor_monitor_loop, daemon=True).start()
        logger.info("Sensor monitor tråd startet OK.")
    except Exception as e:
        logger.error(f"Feil under oppstart av sensor_monitor_loop: {e}", exc_info=True)
        raise

    try:
        logger.info("Registrerer system shutdown-hook (atexit)...")
        atexit.register(shutdown)
        logger.info("Shutdown-hook registrert.")
    except Exception as e:
        logger.warning(f"Kunne ikke registrere shutdown-hook: {e}", exc_info=True)

    try:
        logger.info("Initialiserer MonitorManager...")
        monitor_manager = init_monitor_manager()
        monitor_manager.start_all()
        logger.info("MonitorManager initialisert og alle monitorer startet.")
    except Exception as e:
        logger.error(f"Feil under initialisering av MonitorManager: {e}", exc_info=True)
        raise

    logger.info("=== Systeminitiering fullført ===")


def init_monitor_manager():
    logger.info("Initialiserer MonitorManager...")
    monitor_manager = MonitorManager()
    logger.info("MonitorManager initialisert.")
    return monitor_manager


def shutdown():
    logger.info("=== Starter system shutdown ===")
    pid_file = getattr(paths, "PID_FILE", None)
    try:
        controller = get_controller(None, None, None, None)  # Henter singleton
        controller.shutdown()
        logger.info("GarageController shutdown fullført.")
    except Exception as e:
        logger.error(f"Feil ved GarageController shutdown: {e}", exc_info=True)
        pid_file = getattr(paths, "PID_FILE", None)
    
    if pid_file and os.path.exists(pid_file):
        try:
            logger.debug(f"Sletter pid-fil: {pid_file}")
            os.remove(pid_file)
            logger.info(f"Pid-fil slettet: {pid_file}")
        except Exception as e:
            logger.error(f"Kunne ikke slette pid-fil: {e}", exc_info=True)

    logger.info("=== System shutdown fullført ===")