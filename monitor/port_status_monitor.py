# port_status_monitor.py
"""
monitor/port_status_monitor.py
Monitor for portstatus – overvåker porter via reed-switch sensorer (edge detect).
Bruker get_pi fra utils.pigpio_manager for å sette opp event-callbacks.
"""

import threading
import time
from monitor.monitor_base import MonitorBase
from utils.status_helpers import write_status_file
from utils.pigpio_manager import get_pi, PI_EITHER_EDGE

from utils.logging.unified_logger import get_logger

class PortStatusMonitor(MonitorBase):
    def __init__(self, config):
        logger = get_logger("PortStatusMonitor", category="port_status")
        super().__init__(config, logger)
        self.sensor_pins = config["sensor_pins"]
        self.sensor_config = config["sensor_config"]
        self.timing_config = config.get("timing_config", {})
        self.pi = get_pi()
        self.active_state = self.sensor_config.get("active_state", 0)
        self.pull = self.sensor_config.get("pull", "up")
        self.status_name = "port_status"
        self._status = {}
        self._shutdown_event = threading.Event()
        self._callbacks = []
        self._lock = threading.Lock()
        self._setup_gpio_and_callbacks()
        self.logger.info("PortStatusMonitor initialisert med edge detect.")

    def _setup_gpio_and_callbacks(self):
        # Sett pin modes og pull-ups, og legg på callback for alle sensorpinner
        for port, pins in self.sensor_pins.items():
            for sense_type, pin in pins.items():
                self.pi.set_mode(pin, 0)  # 0 = input
                if self.pull == "up":
                    self.pi.set_pull_up_down(pin, 2)  # 2 = PUD_UP
                elif self.pull == "down":
                    self.pi.set_pull_up_down(pin, 1)
                else:
                    self.pi.set_pull_up_down(pin, 0)
                # Sett opp edge detect callback
                cb = self.pi.callback(pin, PI_EITHER_EDGE, self._sensor_callback)
                self._callbacks.append(cb)
        self.logger.debug("Edge detect-callbacks satt opp på alle port-sensorer.")

    def _sensor_callback(self, gpio, level, tick):
        # Kalles ved hver edge (begge retninger)
        with self._lock:
            status = self._read_ports()
            if status != self._status:
                self.logger.info(f"Portstatus endret (edge): {status}")
                self._status = status
                write_status_file(self.status_name, status)
            self.heartbeat()
            self.logger.debug(f"Edge-detect event på pin {gpio}, level {level}, status: {status}")

    def _read_ports(self):
        result = {}
        for port, pins in self.sensor_pins.items():
            open_pin = pins["open"]
            closed_pin = pins["closed"]
            open_state = self.pi.read(open_pin)
            closed_state = self.pi.read(closed_pin)
            if open_state == self.active_state and closed_state != self.active_state:
                result[port] = "open"
            elif closed_state == self.active_state and open_state != self.active_state:
                result[port] = "closed"
            elif open_state != self.active_state and closed_state != self.active_state:
                result[port] = "moving"
            else:
                result[port] = "error"
        return result

    def start(self):
        self._active = True
        self._shutdown_event.clear()
        self.logger.info("Portstatus-monitor (edge-detect) er aktivert.")

    def get_status(self):
        with self._lock:
            return dict(self._status)  # Returner kopi for sikkerhet

    def shutdown(self):
        self.logger.info("Stopper portstatus-monitor (fjerner callbacks).")
        self._shutdown_event.set()
        for cb in self._callbacks:
            cb.cancel()
        self._callbacks = []
        self._active = False
