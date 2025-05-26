# utils/sensor_monitor.py

import pigpio
from utils.garage_logger import GarageLogger
from utils.pigpio_manager import get_pi



class SensorMonitor:
    def __init__(self, config_gpio, logger=None, pi=None):
        self.logger = logger or GarageLogger() or print
        #self.config_gpio = config_gpio
        self.pi = pi or get_pi()

        print("[DEBUG] pigpio-manager: Initialiserer delt pigpio-instans")
         # Bekreft at pigpio er tilkoblet
        assert self.pi is not None and self.pi.connected, "pigpio ikke tilkoblet"



        if not self.pi or not self.pi.connected:
            raise RuntimeError("Kunne ikke koble til pigpiod")

        self.sensor_pins = config_gpio.get("sensor_pins", {})
        sensor_config = config_gpio.get("sensor_config", {})

        self.active_state = sensor_config.get("active_state", 0)
        pull_mode = {
            "up": pigpio.PUD_UP,
            "down": pigpio.PUD_DOWN,
            "off": pigpio.PUD_OFF
        }.get(sensor_config.get("pull", "up").lower(), pigpio.PUD_UP)

        self.callbacks = {}
        self.callback_function = None

        # Konfigurer alle sensorer
        for port, sensors in self.sensor_pins.items():
            for sensor_type, gpio_pin in sensors.items():
                self.pi.set_mode(gpio_pin, pigpio.INPUT)
                self.pi.set_pull_up_down(gpio_pin, pull_mode)
                self.logger.log_debug("sensor", f"{port} {sensor_type} sensor konfigurert på GPIO {gpio_pin}")

    def set_callback(self, callback_function):
        """
        Setter funksjonen som skal kalles ved sensorendring.
        """
        self.callback_function = callback_function
        self._setup_callbacks()

    def _setup_callbacks(self):
        for port, sensors in self.sensor_pins.items():
            for sensor_type, gpio_pin in sensors.items():
                def callback_func(gpio, level, tick, port=port, sensor_type=sensor_type):
                    if self.callback_function:
                        self.callback_function(
                            gpio=gpio, level=level, tick=tick,
                            port=port, sensor_type=sensor_type
                        )

                cb = self.pi.callback(gpio_pin, pigpio.EITHER_EDGE, callback_func)
                self.callbacks[gpio_pin] = cb
                self.logger.log_debug("sensor", f"Callback registrert for GPIO {gpio_pin}")

    def is_sensor_active(self, port, sensor_type):
        """
        Returnerer True hvis gitt sensor for port er aktiv.
        """
        gpio = self.sensor_pins.get(port, {}).get(sensor_type)
        if gpio is None:
            self.logger.log_warning("sensor", f"Ugyldig sensorforespørsel: {port}/{sensor_type}")
            return False
        level = self.pi.read(gpio)
        return level == self.active_state

    def stop(self):
        """
        Stopper alle registrerte callbacks.
        """
        for gpio, cb in self.callbacks.items():
            cb.cancel()
        self.callbacks.clear()
        self.logger.log_status("sensor", "Alle sensor callbacks fjernet")
