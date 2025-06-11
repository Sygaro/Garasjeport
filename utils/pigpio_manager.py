from utils.logging.unified_logger import get_logger
# utils/pigpio_manager.py

import pigpio

_shared_pi = None
PI_EITHER_EDGE = pigpio.EITHER_EDGE


def get_pi():
    """
    Returnerer en delt pigpio-instans. Oppretter den hvis den ikke finnes.
    """
    global _shared_pi
    if _shared_pi is None:
        _shared_pi = pigpio.pi()
        if not _shared_pi.connected:
            raise RuntimeError("Kunne ikke koble til pigpiod")
    return _shared_pi

def stop_pi():
    """
    Stopper og nullstiller pigpio-instansen ved avslutning.
    """
    global _shared_pi
    if _shared_pi:
        _shared_pi.stop()
        _shared_pi = None
