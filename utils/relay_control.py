from utils.logging.unified_logger import get_logger
# utils/relay_control.py

import time

logger = get_logger("relay_control", category="system")


def trigger(port, pi, relay_pins, relay_config, logger=None):
    """
    Sender en puls til GPIO-pinnen knyttet til gitt port.
    
    Args:
        port (str): Navnet på porten (f.eks. "port1")
        pi (pigpio.pi): pigpio-instans
        relay_pins (dict): mapping fra portnavn til GPIO-pin
        relay_config (dict): må inneholde 'active_state' og 'pulse_duration'
        logger (obj, optional): Logger med .debug() eller ., hvis tilgjengelig
    """
    pin = relay_pins.get(port)
    if pin is None:
        msg = f"[RELAY] Ugyldig portnavn: '{port}' ikke funnet i relay_pins"
        if logger:
            logger.log_error("relay", msg)
        raise ValueError(msg)

    active_state = relay_config.get("active_state", 1)
    pulse_duration = relay_config.get("pulse_duration", 0.4)

    if logger:
        logger.debug(f"Sender puls til {port} (GPIO {pin}) i {pulse_duration:.2f}s")

    pi.write(pin, active_state)
    time.sleep(pulse_duration)
  