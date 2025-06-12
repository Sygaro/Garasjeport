# monitor_manager.py

"""
monitor/monitor_manager.py
Sentral manager for alle monitorer i Garasjeport-systemet.
Starter, stopper og følger opp monitorer, og overvåker deres helsestatus.
Bruker helpers og paths iht. prosjektstandard.
"""

import time
from utils.logging.unified_logger import get_logger
from utils.config_helpers import load_config
from config import config_paths as paths
from monitor.port_status_monitor import PortStatusMonitor
from monitor.env_sensor_monitor import EnvSensorMonitor
from monitor.pigpiod_monitor import PigpiodMonitor


class MonitorManager:
    def __init__(self):
        self.logger = get_logger("MonitorManager", category="system")
        self.monitors = []

        try:
            self.config = load_config("CONFIG_MONITOR_MANAGER_PATH")
            self.port_status_config = load_config("CONFIG_PORT_STATUS_PATH")
            self.env_sensor_config = load_config("CONFIG_SENSOR_ENV_PATH")
            pigpiod_config = load_config("CONFIG_PIGPIOD_MONITOR_PATH")
            self.pigpiod_monitor = PigpiodMonitor(pigpiod_config)
            self.monitors.append(self.pigpiod_monitor)
            self.gpio_config = load_config("CONFIG_GPIO_PATH")
            self.logger.info("Alle monitor-konfigurasjoner lastet inn.")
        except Exception as e:
            self.logger.error(f"Feil under lasting av monitor-konfigurasjon: {e}", exc_info=True)
            raise

        self.heartbeat_timeout = self.config.get("heartbeat_timeout", 15)
        self._init_monitors()


    def _init_monitors(self):
        try:
            port_monitor = PortStatusMonitor(self.gpio_config)
            self.monitors.append(port_monitor)
            self.logger.info("PortStatusMonitor initialisert.")
        except Exception as e:
            self.logger.error(f"Feil under initiering av PortStatusMonitor: {e}", exc_info=True)
        try:
            env_monitor = EnvSensorMonitor(self.env_sensor_config)
            self.monitors.append(env_monitor)
            self.logger.info("EnvSensorMonitor initialisert.")
        except Exception as e:
            self.logger.error(f"Feil under initiering av EnvSensorMonitor: {e}", exc_info=True)

    def start_all(self):
        self.logger.info("Starter alle monitorer.")
        for monitor in self.monitors:
            try:
                monitor.start()
                self.logger.info(f"Monitor {type(monitor).__name__} startet.")
            except Exception as e:
                self.logger.error(f"Feil under oppstart av {type(monitor).__name__}: {e}", exc_info=True)

    def shutdown_all(self):
        self.logger.info("Stopper alle monitorer.")
        for monitor in self.monitors:
            try:
                monitor.shutdown()
                self.logger.info(f"Monitor {type(monitor).__name__} stoppet.")
            except Exception as e:
                self.logger.error(f"Feil under stopp av {type(monitor).__name__}: {e}", exc_info=True)

    def get_status(self):
        """Returnerer status for alle monitorer."""
        status = {}
        for m in self.monitors:
            try:
                status[type(m).__name__] = m.get_status()
            except Exception as e:
                self.logger.error(f"Feil ved uthenting av status fra {type(m).__name__}: {e}", exc_info=True)
        return status

    def health_check(self):
        """Sjekker om alle monitorer lever og svarer innen tidsvindu."""
        now = time.time()
        for monitor in self.monitors:
            if monitor.last_heartbeat is None or (now - monitor.last_heartbeat) > self.heartbeat_timeout:
                self.logger.warning(
                    f"Monitor {type(monitor).__name__} har ikke sendt heartbeat på over {self.heartbeat_timeout} sekunder."
                )
                # Evt. legg til restart eller ekstra tiltak her
