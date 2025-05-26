# utils/relay_control.py

import pigpio
import time
from utils.garage_logger import GarageLogger
from utils.pigpio_manager import get_pi


class RelayControl:
    """
    Håndterer aktivering av relé-pinner via pigpio.
    Brukes til å sende impulser for å åpne/lukke portene.
    """

    def __init__(self, config_gpio, logger=None, pi=None):
        self.config_gpio = config_gpio
        self.logger = logger or GarageLogger() or print
        self.logger.log_debug("relay", "cleanup() kalt")
        self.pi = pi or get_pi()
        print("[DEBUG] pigpio-manager: Initialiserer delt pigpio-instans")


        if not self.pi or not self.pi.connected:
            raise RuntimeError("Kunne ikke koble til pigpiod")

        # Bekreft at pigpio er tilkoblet
        assert self.pi is not None and self.pi.connected, "pigpio ikke tilkoblet"

        # Hent relay-konfig
        self.relay_pins = config_gpio.get("relay_pins", {})
        relay_config = config_gpio.get("relay_config", {})
        self.active_state = relay_config.get("active_state", 0)
        self.pulse_duration = relay_config.get("pulse_duration", 0.4)

        # Konfigurer relé-pins
        for pin in self.relay_pins.values():
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 1 - self.active_state)  # Sett til inaktiv
            self.logger.log_debug("relay", f"GPIO {pin} satt som OUTPUT med inaktiv verdi.")

        self.logger.log_status("relay", f"Reléoppsett fullført: {len(self.relay_pins)} porter")

    def trigger(self, port):
        if port not in self.relay_pins:
            self.logger.log_error("relay", f"Ukjent port: {port}")
            return

        pin = self.relay_pins[port]
        self.logger.log_action(port, "trigger", source="relay_control")

        self.pi.write(pin, self.active_state)
        self.pi.write(pin, 1 - self.active_state)  # umiddelbar reset for enkeltesting
        # For ekte pulsbruk:
        # time.sleep(self.pulse_duration)
        # self.pi.write(pin, 1 - self.active_state)
    
    def cleanup(self):
        if hasattr(self, "_cleanup_done") and self._cleanup_done:
            self.logger.log_debug("relay", "cleanup() allerede kjørt – hopper over.")
            return

        if self.pi and self.pi.connected:
            for pin in self.relay_pins.values():
                self.pi.write(pin, 1 - self.active_state)
            self.logger.log_debug("relay", "RelayControl clean shutdown fullført.")
        else:
            self.logger.log_debug("relay", "RelayControl cleanup hoppet over – pi ikke tilgjengelig.")

        self._cleanup_done = True


    @property
    def pigpio_connected(self):
        return self.pi is not None and self.pi.connected
