from utils.logging.unified_logger import get_logger
# ==========================================
# Filnavn: status.py
# Henter status fra GarageController
# ==========================================

from core.system import controller

def get_port_status(port: str) -> str:
    """
    Returnerer nåværende status for en gitt port.
    """
    return controller.get_current_status(port)
