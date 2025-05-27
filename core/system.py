# core/system.py

import atexit
from config import config_paths as paths
from utils.config_loader import load_config
from utils.pigpio_manager import get_pi, stop_pi
from utils.gpio_initializer import initialize_gpio
from utils.relay_initializer import initialize_relays
from core.garage_controller import GarageController

# Last inn config for sensorer og system
gpio_config = load_config(paths.CONFIG_GPIO_PATH)
system_config = load_config(paths.CONFIG_SYSTEM_PATH)

# Sett opp GPIO-modus og pull for sensorer
initialize_gpio()

# Sett opp reléutganger
relay_pins, relay_config = initialize_relays()

# Start delt pigpio-instans
pi = get_pi()
atexit.register(stop_pi)

# Start GarageController
controller = GarageController(
    config_gpio=gpio_config,
    config_system=system_config,
    relay_pins=relay_pins,
    relay_config=relay_config,
    testing_mode=False
)

# Ryddig nedstenging
def shutdown():
    controller.shutdown()

atexit.register(shutdown)
