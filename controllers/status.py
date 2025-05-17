# ==========================================
# Filnavn: status.py
# Henter status fra GarageController
# ==========================================

from core.garage_controller import GarageController

controller = GarageController()

def get_port_status(port: str) -> str:
    """
    Returnerer nåværende status for en gitt port.
    """
    return controller.get_current_status(port)
