# ==========================================
# Filnavn: system.py
# Felles systemressurser, som controller
# ==========================================

from core.garage_controller import GarageController
import atexit

# Én global instans av GarageController
controller = GarageController()

# Sørg for at GPIO frigjøres på exit
atexit.register(controller.cleanup)
