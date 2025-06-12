# env_sensor_monitor.py
"""
monitor/env_sensor_monitor.py
Monitor for miljøsensor (BME280), arver MonitorBase.
Leser første 'enabled' sensor fra sensors-listen i config_sensor_env.json.
"""

import threading
import time
from monitor.monitor_base import MonitorBase
from utils.status_helpers import write_status_file
from drivers.bme280_sensor import BME280Sensor
from utils.logging.unified_logger import get_logger

class EnvSensorMonitor(MonitorBase):
    def __init__(self, config):
        logger = get_logger("EnvSensorMonitor", category="environment")
        super().__init__(config, logger)
        sensor_conf = self._get_active_sensor(config)
        if not sensor_conf:
            raise ValueError("Ingen aktivert BME280-sensor funnet i config.")
        self.sensor_conf = sensor_conf
        self.driver = BME280Sensor(sensor_conf)
        self.interval = sensor_conf.get("interval_sec", 10)
        self._thread = None
        self._status = {}
        self._shutdown_event = threading.Event()
        self.status_name = f"env_sensor_{sensor_conf['id']}"

    def _get_active_sensor(self, config):
        sensors = config.get("sensors", [])
        for s in sensors:
            if s.get("enabled", False) and s.get("type") == "BME280":
                return s
        return None

    def start(self):
        self._active = True
        self._shutdown_event.clear()
        self.logger.info(f"Starter miljøsensor-monitor for {self.status_name}.")
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def _monitor_loop(self):
        while not self._shutdown_event.is_set():
            try:
                status = self.driver.read_data()
                self._status = status
                write_status_file(self.status_name, status)
                self.heartbeat()
                self.logger.debug(f"Oppdatert miljøsensor-data: {status}")
            except Exception as e:
                self.logger.error(f"Feil under miljøsensor-monitorering: {e}", exc_info=True)
            time.sleep(self.interval)

    def get_status(self):
        return self._status

    def shutdown(self):
        self.logger.info(f"Stopper miljøsensor-monitor for {self.status_name}.")
        self._shutdown_event.set()
        self.logger.debug("Venter på at monitor-tråden skal avslutte...")
        if self._thread and self._thread.is_alive():
            self.logger.debug("Monitor-tråden er fortsatt aktiv, venter på avslutning...")  
            self._thread.join(timeout=3)
            if self._thread.is_alive():
                self.logger.warning("Monitor-tråden avsluttet ikke i tide, fortsetter likevel.")
        self.logger.info(f"Miljøsensor-monitor for {self.status_name} stoppet.")
        self._active = False
