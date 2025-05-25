# utils/pigpio_manager.py

import pigpio

_pi_instance = None

def get_pi():
    """
    Returnerer en delt pigpio-instans. Oppretter den hvis den ikke finnes.
    """
    global _pi_instance
    if _pi_instance is None:
        _pi_instance = pigpio.pi()
        if not _pi_instance.connected:
            raise RuntimeError("Kunne ikke koble til pigpiod")
    return _pi_instance

def stop_pi():
    """
    Stopper og nullstiller pigpio-instansen ved avslutning.
    """
    global _pi_instance
    if _pi_instance:
        _pi_instance.stop()
        _pi_instance = None
