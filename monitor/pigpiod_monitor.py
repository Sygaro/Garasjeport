# pigpiod_monitor.py
"""
monitor/pigpiod_monitor.py
Monitor for pigpiod-tjenesten (kontrollerer at pigpiod kjører og svarer).
Arver MonitorBase, følger felles struktur og logger alt relevant.
"""

import threading
import time
from monitor.monitor_base import MonitorBase
from utils.status_helpers import write_status_file
from utils.pigpio_manager import get_pi
from utils.logging.unified_logger import get_logger

class PigpiodMonitor(MonitorBase):
    def __init__(self, config):
        logger = get_logger("PigpiodMonitor", category="system", source="pigpiod_monitor")
        super().__init__(config, logger)
        self.interval = config.get("interval", 10)
        self._thread = None
        self._status = {}
        self._shutdown_event = threading.Event()
        self.status_name = "pigpiod_monitor"
        self.logger.info("PigpiodMonitor initialisert.")

    def start(self):
        self._active = True
        self._shutdown_event.clear()
        self.logger.info("Starter pigpiod-monitor.")
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def _monitor_loop(self):
        while not self._shutdown_event.is_set():
            status = self._check_pigpiod()
            self._status = status
            write_status_file(self.status_name, status)
            self.heartbeat()
            if status.get("pigpiod_status") != "ok":
                self.logger.error(f"pigpiod-feil: {status}")
            else:
                self.logger.debug(f"pigpiod OK: {status}")
            time.sleep(self.interval)

    def _check_pigpiod(self):
        try:
            pi = get_pi()
            connected = getattr(pi, "connected", None)
            # pigpio.pi.connected skal være 1 hvis OK
            if connected == 1:
                status = {"pigpiod_status": "ok", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
            else:
                status = {"pigpiod_status": "disconnected", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
            return status
        except Exception as e:
            self.logger.error(f"Feil ved pigpiod-sjekk: {e}", exc_info=True)
            return {"pigpiod_status": "error", "error": str(e), "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

    def get_status(self):
        return self._status

    def shutdown(self):
        self.logger.info("Stopper pigpiod-monitor.")
        self._shutdown_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        self._active = False
        self.logger.info("Pigpiod-monitor stoppet.")