# ==========================================
# Filnavn: system.py
# Felles systemressurser, som controller
# ==========================================

from utils.config_loader import load_config
from core.garage_controller import GarageController
import atexit

# Én global instans av GarageController

# Last inn konfigurasjoner fra config/*.json
config_gpio, config_system = load_config()

controller = GarageController(config_gpio, config_system, testing_mode=False)
