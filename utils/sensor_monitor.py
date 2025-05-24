import pigpio
from config import config_paths as paths
from utils.garage_logger import GarageLogger


class SensorMonitor:
    def __init__(self, config_gpio, logger=None):
        self.config_gpio = config_gpio
        self.sensor_pins = config_gpio.get("sensor_pins", {})
        self.sensor_config = config_gpio.get("sensor_config", {})
        self.logger = logger or GarageLogger()

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Kunne ikke koble til pigpiod")

        self.callback_function = None
        self.callbacks = {}

        self._validate_sensor_config()
        self._setup_callbacks()

    def _validate_sensor_config(self):
        if not self.sensor_pins:
            raise ValueError("Ingen 'sensor_pins' definert i config_gpio")

        for port, sensors in self.sensor_pins.items():
            if not isinstance(sensors, dict):
                raise ValueError(f"Ugyldig format for sensors i port '{port}'")
            if "open" not in sensors or "closed" not in sensors:
                raise ValueError(f"Port '{port}' mangler 'open' eller 'closed' sensor")

    def set_callback(self, callback_function):
        """
        Setter ekstern callback som skal kalles når en sensor endrer tilstand.
        """
        self.callback_function = callback_function

    def _setup_callbacks(self):
        for port, sensors in self.sensor_pins.items():
            for sensor_type in ["open", "closed"]:
                gpio_pin = sensors.get(sensor_type)
                if gpio_pin is None:
                    self.logger.log_error("sensor_monitor", f"GPIO-pin ikke definert for {port} - {sensor_type}")
                    continue

                self.pi.set_mode(gpio_pin, pigpio.INPUT)

                pull = self.sensor_config.get("pull", "up").lower()
                if pull == "up":
                    self.pi.set_pull_up_down(gpio_pin, pigpio.PUD_UP)
                elif pull == "down":
                    self.pi.set_pull_up_down(gpio_pin, pigpio.PUD_DOWN)

                callback = self._create_callback(gpio_pin, port, sensor_type)
                self.callbacks[gpio_pin] = self.pi.callback(gpio_pin, pigpio.EITHER_EDGE, callback)

                self.logger.log_status("sensor_monitor", f"Callback aktivert for {port} - {sensor_type} (GPIO {gpio_pin})")

    def _create_callback(self, gpio_pin, port, sensor_type):
        def callback_func(gpio, level, tick):
            if self.callback_function:
                self.callback_function(gpio=gpio, level=level, tick=tick, port=port, sensor_type=sensor_type)
        return callback_func

    def stop(self):
        for cb in self.callbacks.values():
            cb.cancel()
        self.pi.stop()
        self.logger.log_status("sensor_monitor", "SensorMonitor stoppet og GPIO-ressurser frigjort.")
