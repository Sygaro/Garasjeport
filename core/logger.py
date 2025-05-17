# ==========================================
# Filnavn: logger.py
# Modul for logging av garasjeport-aktivitet
# Logger: hendelser, statusendringer, feil, tid
# ==========================================

import os
import logging
from datetime import datetime

# Opprett logs-mappen hvis den ikke finnes
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Funksjon som oppretter en logger med gitt navn og fil
def _setup_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(os.path.join(LOG_DIR, filename))
    formatter = logging.Formatter('%(asctime)s | %(message)s', "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

class GarageLogger:
    """
    Logger for garasjesystemet. Skriver til fire loggfiler:
    - activity.log: motorpulser og brukerhandlinger
    - status.log: endringer i portstatus
    - errors.log: sensorfeil eller blokkert bevegelse
    - timing.log: tid brukt ved åpning/lukking
    """

    def __init__(self):
        self.activity_logger = _setup_logger('activity_logger', 'activity.log')
        self.status_logger = _setup_logger('status_logger', 'status.log')
        self.error_logger = _setup_logger('error_logger', 'errors.log')
        self.timing_logger = _setup_logger('timing_logger', 'timing.log')

    def log_action(self, port, action, source='unknown', result='success'):
        """
        Logger en brukerhandling (eks. åpne/lukke via API, app, Homey).
        """
        msg = f"{port} | action={action} | source={source} | result={result}"
        self.activity_logger.info(msg)

    def log_status_change(self, port, new_status):
        """
        Logger en endring i portstatus (åpen, lukket, bevegelse, feil).
        """
        msg = f"{port} | status_changed_to={new_status}"
        self.status_logger.info(msg)

        if new_status == 'sensor_error':
            self.error_logger.error(f"{port} | SENSOR ERROR detected")

    def log_timing(self, port, direction, duration):
        """
        Logger tidsbruk på åpning/lukking av port.
        """
        msg = f"{port} | {direction} | duration={duration:.2f}s"
        self.timing_logger.info(msg)
