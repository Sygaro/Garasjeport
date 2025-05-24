import pigpio
import time

class RelayControl:
    """
    Håndterer aktivering av relé-pinner via pigpio.
    Brukes til å sende impulser for å åpne/lukke portene.
    """

    def __init__(self, config_gpio):
        self.config_gpio = config_gpio
        self.pi = pigpio.pi()
        print(f"[DEBUG] pigpio connected: {self.pi.connected}")
        self.relay_pins = self.config_gpio.get("relay_pins", {})


        if not self.pi.connected:
            raise RuntimeError("Kunne ikke koble til pigpiod")

        self.relay_pins = config_gpio["relay_pins"]
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
        Setter alle pinner til inaktiv og lukker pigpio-forbindelsen.
        """
        for pin in self.relay_pins.values():
            self.pi.write(pin, 1 - self.active_state)
        self.pi.stop()

    

@property
def pigpio_connected(self):
    return self.pi is not None and self.pi.connected
