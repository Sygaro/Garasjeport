# ==========================================
# Filnavn: system.py
# Felles systemressurser, som controller
# ==========================================
from config import config_paths as paths
from utils.config_loader import load_config
from core.garage_controller import GarageController
import atexit

# Én global instans av GarageController

# Last inn konfigurasjoner fra config/*.json
#config_gpio, config_system = load_config()
gpio_config = load_config(paths.CONFIG_GPIO_PATH)
system_config = load_config(paths.CONFIG_SYSTEM_PATH)

# Én global instans av controller
controller = GarageController(gpio_config, system_config, testing_mode=False)

# Sørg for ryddig nedstenging
def shutdown():
    controller.shutdown()

atexit.register(shutdown)
