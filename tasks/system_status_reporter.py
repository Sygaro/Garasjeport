# system_status_reporter.py
"""
tasks/system_status_reporter.py
Henter og rapporterer samlet systemstatus fra MonitorManager (ny struktur).
Logger alle hendelser og kan lagre rapport om ønskelig.
"""

import time
import threading
from monitor.monitor_manager import MonitorManager
from utils.logging.unified_logger import get_logger
from utils.status_helpers import read_status_file

REPORT_INTERVAL = 60  # Skriv statusrapport hvert minutt – tilpass etter behov

logger = get_logger("SystemStatusReporter", category="system", source="system_status_reporter")

class SystemStatusReporter:
    def __init__(self, monitor_manager: MonitorManager, interval: int = REPORT_INTERVAL):
        self.monitor_manager = monitor_manager
        self.interval = interval
        self._thread = None
        self._shutdown_event = threading.Event()

    def start(self):
        logger.info("Starter SystemStatusReporter.")
        self._shutdown_event.clear()
        self._thread = threading.Thread(target=self._report_loop, daemon=True)
        self._thread.start()

    def _report_loop(self):
        while not self._shutdown_event.is_set():
            try:
                # Hent status for alle monitorer
                status = self.monitor_manager.get_status()
                # Alternativ: Les statusfiler direkte hvis ønskelig (f.eks. status/port_status.json)
                # status = {
                #    "port_status": read_status_file("port_status"),
                #    "env_sensor_bme1": read_status_file("env_sensor_bme1"),
                #    "pigpiod_monitor": read_status_file("pigpiod_monitor"),
                # }
                logger.info(f"Systemstatus: {status}")
                # Evt. lagre rapport til fil
                # with open("status/system_report.json", "w") as f:
                #     json.dump(status, f, indent=2)
            except Exception as e:
                logger.error(f"Feil ved uthenting av systemstatus: {e}", exc_info=True)
            time.sleep(self.interval)

    def shutdown(self):
        logger.info("Stopper SystemStatusReporter.")
        self._shutdown_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)

# Eksempel på bruk:
if __name__ == "__main__":
    mm = MonitorManager()
    reporter = SystemStatusReporter(monitor_manager=mm, interval=60)
    mm.start_all()
    reporter.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        reporter.shutdown()
        mm.shutdown_all()
        logger.info("Systemstatus og monitorer stoppet.")
