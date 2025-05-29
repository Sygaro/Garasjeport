# utils/sensor_monitor.py

import pigpio
from utils.logging.logger_manager import get_logger
from config.config_paths import CONFIG_GPIO_PATH
from utils.file_utils import load_json

logger = get_logger("sensor_monitor")

class SensorMonitor:
    def __init__(self, config_gpio, logger=None, pi=None):
        """
        Overvåker porter og registrerer sensor-endringer via pigpio edge detection.
        """
        self.pi = pi  # Delt pigpio-instans (fra pigpio_manager.get_pi())
        self.logger = logger or get_logger("sensor_monitor", category="sensor")
        self.logger.info("SensorMonitor startet")

        self.config = config_gpio or load_json(CONFIG_GPIO_PATH)

        self.sensor_config = self.config.get("sensor_config", {})
        self.sensor_pins = self.config.get("sensor_pins", {})

        self.active_state = self.sensor_config.get("active_state", 1)
        self._gpio_to_port = {}     # GPIO: (portnavn, sensor_type)
        self.callback_function = None
        self.callbacks = []

        self._build_gpio_mapping()

    def _build_gpio_mapping(self):
        """
        Lager oppslagstabell for GPIO → (port, sensor_type)
        """
        for port, sensors in self.sensor_pins.items():
            for sensor_type, gpio in sensors.items():
                self._gpio_to_port[gpio] = (port, sensor_type)

    def set_callback(self, callback_function):
        """
        Registrerer ekstern callback som trigges ved sensorendring.
        """
        self.callback_function = callback_function
        self.logger.debug("Callback-funksjon registrert")
        self._setup_callbacks()

    def _setup_callbacks(self):
        """
        Registrerer pigpio edge detection callbacks for alle sensorer.
        Forutsetter at pinnene er initialisert via gpio_initializer.
        """
        for gpio, (port, sensor_type) in self._gpio_to_port.items():
            try:
                cb = self.pi.callback(
                    gpio,
                    pigpio.EITHER_EDGE,
                    self._generate_handler(gpio)
                )
                self.callbacks.append(cb)
                self.logger.log_debug(
                    "sensor_monitor",
                    f"Callback satt på port: {port}, sensor: {sensor_type}, GPIO: {gpio}"
                )
            except Exception as e:
                self.logger.error(f"Feil ved registrering av callback på GPIO {gpio}: {e}")

    def _generate_handler(self, gpio):
        """
        Lager handler som kaller _handle_sensor med korrekt GPIO.
        """
        return lambda gpio, level, tick: self._handle_sensor(gpio, level)

    def _handle_sensor(self, gpio, level):
        """
        Behandler sensorendring og videresender til registrert callback.
        """
        if gpio not in self._gpio_to_port:
            self.logger.log_warning("sensor_monitor", f"Ukjent GPIO: {gpio} – finnes ikke i konfig")
            return

        port, sensor_type = self._gpio_to_port[gpio]
        active_text = "aktiv" if level == self.active_state else "inaktiv"

        self.logger.log_debug(
            "sensor_monitor",
            f"Sensor-endring: {port} ({sensor_type}) GPIO {gpio} = {level} → {active_text}"
        )

        if self.callback_function:
            self.callback_function(port, sensor_type, level)
        else:
            self.logger.log_warning("sensor_monitor", "Ingen callback-funksjon satt – ignorerer signal")

    def cleanup(self):
        """
        Stopper alle pigpio callbacks og rydder opp.
        """
        for cb in self.callbacks:
            cb.cancel()
        self.callbacks.clear()

        self.logger.debug("Alle sensor-callbacks er deaktivert og fjernet")
