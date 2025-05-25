import pigpio
import time
from utils.garage_logger import GarageLogger

class RelayControl:
    """
    Håndterer aktivering av relé-pinner via pigpio.
    Brukes til å sende impulser for å åpne/lukke portene.
    """

    def __init__(self, config_gpio, logger=None, pi=None):
        self.logger = logger or print
        self.pi = pi
        self.config_gpio = config_gpio
        #print(f"[DEBUG] pigpio connected: {self.pi.connected}")
        self.logger = logger or GarageLogger()
        self.relay_pins = self.config_gpio.get("relay_pins", {})

        self.relay_control = RelayControl(config_gpio, self.pi, logger=self.logger)
        self.sensor_monitor = SensorMonitor(config_gpio, self.logger, self.pi)

        
        if not self.pi.connected:
            raise RuntimeError("Kunne ikke koble til pigpiod")

        self.active_state = config_gpio["relay_config"]["active_state"]
        self.pulse_duration = config_gpio["relay_config"]["pulse_duration"]

        for pin in self.relay_pins.values():
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 1 - self.active_state)  # Sett inaktiv

    def trigger(self, port):
        """
        Sender puls til portens relé.
        """
        pin = self.relay_pins[port]
        self.pi.write(pin, self.active_state)
        time.sleep(self.pulse_duration)
        self.pi.write(pin, 1 - self.active_state)

    def cleanup(self):
        """
        Frigjør pigpio-ressurser for relekontroll.
        """
        try:
            self.logger.log_status("relay_control", "Rydder opp pigpio-tilkobling")
            self.pi.stop()
        except Exception as e:
            self.logger.log_error("relay_control", f"Feil ved cleanup: {e}")

    @property
    def pigpio_connected(self):
        return self.pi is not None and self.pi.connected
