# ==========================================
# Filnavn: system.py
# Felles systemressurser, som controller
# ==========================================

from core.garage_controller import GarageController
import atexit,pigpio

# Én global instans av GarageController
controller = GarageController()
 

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Kunne ikke koble til pigpiod – start med sudo pigpiod")
