# core/system_init.py

"""
core/system_init.py (utdrag for monitor-integrasjon)
Integrerer MonitorManager i system-initiering og shutdown.
Bruker prosjektets standard for import av paths.
"""

import os, threading, atexit
from utils.logging.unified_logger import get_logger
from core.system import get_controller
from config import config_paths as paths
from monitor.monitor_manager import MonitorManager
from utils.config_helpers import load_config



logger = get_logger("system_init", category="system")



def init():
    logger.info("=== Starter systeminitiering ===")

    # Last konfigurasjoner fra fil via paths
    try:
        config_gpio = load_config("CONFIG_GPIO_PATH")
        config_port_status = load_config("CONFIG_PORT_STATUS_PATH")
        relay_pins = config_gpio.get("relay_pins") or []  # eller bruk riktig nøkkel
        relay_config = config_gpio.get("relay_config") or {}  # eller bruk riktig nøkkel
    except Exception as e:
        logger.error(f"Feil ved lasting av konfigurasjon: {e}", exc_info=True)
        raise

    try:
        controller = get_controller(
            config_gpio=config_gpio,
            config_port_status=config_port_status,
            relay_pins=relay_pins,
            relay_config=relay_config,
        )
        logger.info("GarageController initialisert OK.")
    except Exception as e:
        logger.error(f"Feil under initiering av GarageController: {e}", exc_info=True)
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