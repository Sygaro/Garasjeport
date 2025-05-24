import pigpio
import threading
import time
import logging

logger = logging.getLogger(__name__)

class SensorMonitor:
    def __init__(self, port_config, sensor_event_handler):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Kunne ikke koble til pigpiod")

        self.callbacks = []
        self.sensor_event_handler = sensor_event_handler
        self.port_config = port_config  # from config_gpio.json
        self._setup_callbacks()

    def _setup_callbacks(self):
        for port, sensors in self.port_config.items():
            for sensor_type in ["open", "closed"]:
                gpio_pin = sensors[sensor_type]
                self.pi.set_mode(gpio_pin, pigpio.INPUT)
                self.pi.set_pull_up_down(gpio_pin, pigpio.PUD_UP)

                callback = self.pi.callback(
                    gpio_pin,
                    pigpio.EITHER_EDGE,
                    self._create_callback(port, sensor_type)
                )
                self.callbacks.append(callback)
                logger.info(f"Callback satt for {port} - {sensor_type} på GPIO {gpio_pin}")

    def _create_callback(self, port, sensor_type):
        def handler(gpio, level, tick):
            if level == pigpio.TIMEOUT:
                return
            state = "HIGH" if level == 1 else "LOW"
            logger.debug(f"Sensor {sensor_type} for {port} endret til {state}")
            self.sensor_event_handler(port, sensor_type, level)
        return handler

    def stop(self):
        for cb in self.callbacks:
            cb.cancel()
        self.pi.stop()
