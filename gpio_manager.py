# gpio_manager.py
import lgpio

class GPIOManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GPIOManager, cls).__new__(cls)
            cls._instance.chip = lgpio.gpiochip_open(0)
            cls._instance.claimed_pins = set()
        return cls._instance

    def claim_output(self, pin):
        if pin not in self.claimed_pins:
            lgpio.gpio_claim_output(self.chip, pin)
            self.claimed_pins.add(pin)

    def claim_input(self, pin):
        if pin not in self.claimed_pins:
            lgpio.gpio_claim_input(self.chip, pin)
            self.claimed_pins.add(pin)

    def write(self, pin, value):
        lgpio.gpio_write(self.chip, pin, value)

    def read(self, pin):
        return lgpio.gpio_read(self.chip, pin)

    def cleanup(self):
        for pin in self.claimed_pins:
            lgpio.gpio_free(self.chip, pin)
        lgpio.gpiochip_close(self.chip)
