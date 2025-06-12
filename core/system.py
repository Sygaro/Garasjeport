# core/system.py

import atexit

from utils.logging.unified_logger import get_logger
from monitor.monitor_manager import MonitorManager
from tasks.system_status_reporter import SystemStatusReporter
from config import config_paths as paths
from utils.config_loader import load_config
from utils.pigpio_manager import get_pi, stop_pi
from system.gpio_initializer import initialize_gpio
from utils.relay_initializer import initialize_relays
from core.garage_controller import GarageController

logger = get_logger("system_init", category="system")


monitor_manager = MonitorManager()
reporter = SystemStatusReporter(monitor_manager, interval=60)
reporter.start()

# Last inn config for sensorer og system
gpio_config = load_config(paths.CONFIG_GPIO_PATH)
config_port_status = load_config(paths.CONFIG_PORT_STATUS_PATH)

# Sett opp GPIO-modus og pull for sensorer
initialize_gpio()
logger.info("GPIO-modus og pull satt opp for sensorer")

# Sett opp reléutganger
relay_pins, relay_config = initialize_relays()
logger.info("Reléutganger satt opp")
# Start delt pigpio-instans
pi = get_pi()
logger.info("Delt pigpio-instans startet")
# Registrer stopp av pigpio-instans ved nedstenging
atexit.register(stop_pi)

# Start GarageController
controller = GarageController(
    config_gpio=gpio_config,
    config_port_status=config_port_status,
    relay_pins=relay_pins,
    relay_config=relay_config,
)
logger.info("GarageController initialisert")

reporter.start()
logger.info("System status reporter startet")

_controller = None

def get_controller(config_gpio, config_port_status, relay_pins, relay_config):
    global _controller
    if _controller is None:
        from core.garage_controller import GarageController
        _controller = GarageController(
            config_gpio=config_gpio,
            config_port_status=config_port_status,
            relay_pins=relay_pins,
            relay_config=relay_config,
        )
    return _controller

# Ryddig nedstenging
def shutdown():

    logger.info("=== Starter system nedstenging ===") 
    controller.shutdown()
    reporter.shutdown()
    logger.info("System status reporter stoppet")


atexit.register(shutdown)
